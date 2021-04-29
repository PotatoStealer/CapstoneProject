from flask import Flask, render_template, request
from sql_utils import database, fetch_description, fetch_service_description, fetch_service_stops
from utils import bestStartEndGuess, clean
import re

app = Flask(__name__)

def routes(busstopcode):
    cursor = database().cursor()
    cursor.execute('''SELECT DISTINCT bus_services.ServiceNo, bus_services.Direction, bus_services.OriginCode, 
                             bus_services.DestinationCode, bus_services.LoopDesc
                    FROM bus_routes 
                    INNER JOIN bus_services ON bus_services.ServiceNo=bus_routes.ServiceNo 
                    AND bus_routes.Direction=bus_services.Direction 
                    WHERE BusStopCode=?;''', (busstopcode,))
    return cursor.fetchall()

@app.route("/")
def index():
    return render_template("main_page.html")


def natSort(arr):
    '''
    A lacklustre and hardcoded replica of natural sorting relying on the insertion sort algorithm.
    This is used for arranging data in lists given that the first element is the key.

    :param arr: Input array
    :return: Sorted array
    '''
    for i in range(1, len(arr)):
        pivot = arr[i]
        pos = i
        while pos > 0 and int(re.findall('\d+', arr[pos-1][0])[0]) > int(re.findall('\d+', pivot[0])[0]):
            arr[pos] = arr[pos-1]
            pos -= 1
        arr[pos] = pivot
    return arr

@app.route("/route_through_stop")
def route_through_stop():
    if request.args.get("busstopcode", None):
        busstopcode = clean(request.args["busstopcode"])
        fetch = routes(busstopcode)
        if len(fetch):
            display = []
            for dat in fetch:
                origin = fetch_description(dat[2])
                if not len(dat[4]):
                    destination = fetch_description(dat[3])
                else:
                    destination = dat[4] + " (Loop)"
                display.append([dat[0], origin, destination, dat[1]])
            return render_template("route_through_stop.html", display=natSort(display), busstopcode=busstopcode)
        return render_template("route_through_stop.html", display=[], busstopcode=0)
    return render_template("route_through_stop.html", display=[], busstopcode=None)


@app.route('/bus_service')
def bus_service():
    def prettify_service_info(service_no):
        '''
        Convenience method for sanitising and preparing service information for a bus service
        :param service_no: Input service number
        :return: Prettified strings :D
        '''
        info = []
        for row in fetch_service_description(service_no):
            if not len(row[4]):
                info.append([row[0], row[1], fetch_description(row[2]), fetch_description(row[3])])
            else:
                info.append([row[0], row[1], row[2], row[4] + " (Loop)"])
        return info

    if request.args.get("service_no", None):
        service_no = clean(request.args["service_no"])
        if not request.args.get("direction", None):
            return render_template("bus_service.html", service_no=service_no, info=prettify_service_info(service_no))
        else:
            direction = clean(request.args["direction"])
            return render_template("bus_service.html", service_no=service_no, stops=fetch_service_stops(service_no, direction))

    return render_template("bus_service.html")

@app.route('/route_planner')
def route_planner():
    WARN_NONEXACT = "We can't find an exact match, but we think you wanted to travel from {} to {}"
    WARN_INPUT_MISSING = "Please input both your starting location and your destination."
    WARN_NOSTOPS = "We are unable to find any routes :( Perhaps try refine your search?"

    if request.args.get("origin", None) and request.args.get("destination", None):
        origin, destination = request.args["origin"], request.args["destination"]
        if not (len(origin) <= 30 and len(destination) <= 30):
            return render_template('route_planner.html', info=[], warn=WARN_NOSTOPS)

        guesses = bestStartEndGuess(origin, destination)

        if not guesses:
            return render_template('route_planner.html', warn=WARN_NOSTOPS)

        # Unpack the predicted values and its search score
        origin, r1 = guesses[0][0], guesses[0][1]
        destination, r2 = guesses[1]
        services = guesses[2]
        error = ""
        info = []
        cursor = database().cursor()
        for service in services:
            cursor.execute('''SELECT ServiceNo, Direction, OriginCode, DestinationCode, LoopDesc
                                                FROM bus_services
                                                WHERE ServiceNo=? AND Direction=?''', (service[0],service[1]))
            options = cursor.fetchall()
            for display in options:
                if not len(display[4]):
                    info.append([display[0], display[1], fetch_description(display[2]), fetch_description(display[3])])
                else:
                    info.append([display[0], display[1], fetch_description(display[2]), display[4] + " (Loop)"])

        if r1 <= 75 or r2 <= 75:
            error = WARN_NONEXACT.format(origin, destination)

        return render_template('route_planner.html', info=natSort(info), warn=error)
    else:
        return render_template('route_planner.html', warn=WARN_INPUT_MISSING)

app.run()