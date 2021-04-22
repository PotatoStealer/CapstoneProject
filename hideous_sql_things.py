import sqlite3
import json

connection = sqlite3.connect("bus_data.db", check_same_thread=False)

def database():
    return connection

def insert_data():
    cursor = database().cursor()
    paths = ["bus_routes.json", "bus_services.json", "bus_stops.json"]
    for path in paths:
        with open(path, "r", encoding="utf8") as f:
            table_name = path.split(".")[0]
            cursor.execute(f'''DELETE FROM {table_name}''')
            data = json.load(f)
            for row in data:
                columns = ', '.join(row.keys())
                placeholders = ":"+', :'.join(row.keys())
                query = f'''INSERT INTO "{table_name}" (%s) VALUES (%s)''' % (columns, placeholders)
                cursor.execute(query, row)
            database().commit()

def fetch_all_stops():
    cursor = database().cursor()
    cursor.execute('''SELECT DISTINCT Description FROM bus_stops''')
    return [ent[0] for ent in cursor.fetchall()]

def fetch_description(busstopcode):
    cursor = database().cursor()
    return cursor.execute('''SELECT Description FROM bus_stops WHERE BusStopCode=?''', (busstopcode,)).fetchone()[0]

def fetch_service_description(service_no):
    cursor = database().cursor()
    cursor.execute('''SELECT ServiceNo, Direction, OriginCode, DestinationCode, LoopDesc
                                    FROM bus_services
                                    WHERE ServiceNo=?''', (service_no,))
    return cursor.fetchall()

def fetch_service_stops(service_no, direction):
    cursor = database().cursor()
    cursor.execute('''SELECT bus_routes.StopSequence, bus_routes.BusStopCode, bus_stops.Description, bus_routes.Distance
                                                    FROM bus_routes
                                                    INNER JOIN bus_stops ON bus_routes.BusStopCode=bus_stops.BusStopCode
                                                    WHERE bus_routes.ServiceNo=? AND bus_routes.Direction=?;''',
                   (service_no, direction))
    return cursor.fetchall()
