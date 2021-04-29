from fuzzywuzzy import fuzz, process
from sql_utils import fetch_all_stops, database
import time

PUNCTUATION_BLACKLIST = r"""!'"$%&();<=>?"""

def clean(search: str):
    return search.lower().translate(str.maketrans('', '', PUNCTUATION_BLACKLIST))

def routes(busstopcode):
    cursor = database().cursor()
    cursor.execute('''SELECT bus_services.ServiceNo, bus_services.Direction, bus_services.OriginCode, 
                             bus_services.DestinationCode, bus_services.LoopDesc
                    FROM bus_routes 
                    INNER JOIN bus_services ON bus_services.ServiceNo=bus_routes.ServiceNo 
                    AND bus_routes.Direction=bus_services.Direction 
                    WHERE BusStopCode=?;''', (busstopcode,))
    return cursor.fetchall()

def stop_with_description(description):
    cursor = database().cursor()
    cursor.execute('''SELECT bus_stops.BusStopCode FROM bus_stops WHERE Description=?''', (description,))
    return cursor.fetchone()

def stop_description(busstopcode):
    cursor = database().cursor()
    cursor.execute('''SELECT bus_stops.Description FROM bus_stops WHERE BusStopCode=?''', (busstopcode,))
    return cursor.fetchone()

def route_through_stops(origin: int, destination: int):
    if not routes(str(origin)) or not routes(str(destination)):
        return None
    else:
        return [(stop_description(origin), 100), (stop_description(destination), 100), set(routes(origin)) & set(routes(destination))]

def bestStartEndGuess(origin: str, destination: str, guess_limit=30, guess_threshold=70, certainty_threshold=88):
    """
    For the Route Planner feature. Includes logic to account for poor naming decisions by LTA causing
    bad guesses by fuzzywuzzy.

    This is slightly non-performant since the process limit is set to 20 instead of the default 5. This almost guarantees that the
    desired guess falls into the top 20 guesses.

    If the fuzz score for both inputs are below the guess_threshold, None is returned.

    If the fuzz score for both inputs above the guess_threshold,
    :param origin: User input for origin stop. Can be a bus stop code or a text description
    :param destination: User input for destination stop. Can be a bus stop code or a text description
    :param guess_limit: Maximum number of guesses produced
    :param guess_threshold: Minimum score for a guess to be considered. Defaults to the magic value of 69.
    :param certainty_threshold: Minimum score for a guess to be considered "certain". Defaults to 88.
    :return: A list containing [(origin_description, org_score), (destination_description, dest_score), set(routes)]
    """
    all_stops = fetch_all_stops()
    origin, destination = clean(origin), clean(destination)

    '''Produces a list of guesses arranged by the fuzz score in descending order.'''
    origin_guess = process.extract(origin, all_stops, limit=guess_limit)
    destination_guess = process.extract(destination, all_stops, limit=guess_limit)

    # We can't produce a good enough guess
    if origin_guess[0][1] < guess_threshold and destination_guess[0][1] < guess_threshold:
        return None

    # If we are certain of either one of the guesses
    else:
        # Word count. Reject guesses that don't contain the same number of words as user input.
        # such as Serangoon Int (input) being matched to Sembawang Int/Opp Blk 315 (guess).
        # This is because the input is actually referred to as S'Goon Int in the dataset,
        # which no self-respecting user would actually know or care about.
        for i in range(len(origin_guess) - 1, -1, -1):
            if len(origin_guess[i][0].split(" ")) != len(origin.split(" ")):
                origin_guess.pop(i)

        for i in range(len(destination_guess) - 1, -1, -1):
            if len(destination_guess[i][0].split(" ")) != len(destination.split(" ")):
                destination_guess.pop(i)

        if not len(origin_guess) or not len(destination_guess):
            return None

        origin_guess = sorted(
            list(zip(origin_guess, map(lambda x: fuzz.partial_ratio(origin, clean(x[0])) * x[1] / 100, origin_guess))),
            key=lambda y: y[1], reverse=True)
        destination_guess = sorted(
            list(zip(destination_guess, map(lambda x: fuzz.partial_ratio(destination, clean(x[0])) * x[1] / 100, destination_guess))),
            key=lambda y: y[1], reverse=True)

        # If we are certain or uncertain of both, then choose the best match
        if (origin_guess[0][0][1] >= certainty_threshold and destination_guess[0][0][1] >= certainty_threshold) \
                or (origin_guess[0][0][1] < certainty_threshold and destination_guess[0][0][1] < certainty_threshold):
            services = set(routes(stop_with_description(origin_guess[0][0][0])[0])) & \
                       set(routes(stop_with_description(destination_guess[0][0][0])[0]))
            return [origin_guess[0][0], destination_guess[0][0], services]

        # Else, we make further guesses based on the initial guess with a lower fuzz score
        else:
            if origin_guess[0][0][1] >= destination_guess[0][0][1]:
                pivot = origin_guess[0][0]
                choice = destination_guess
                check = 1
            else:
                pivot = destination_guess[0][0]
                choice = origin_guess
                check = 0

            # If there is a service between any two stops
            # Here, choice is sorted in descending order of the scorer ratio
            for entry in choice:
                services = set(routes(stop_with_description(pivot[0])[0])) & \
                           set(routes(stop_with_description(entry[0][0])[0]))
                if services:
                    if check:
                        return [pivot, entry, services]
                    else:
                        return [entry, pivot, services]
            return None
