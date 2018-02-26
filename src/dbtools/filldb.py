import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from subprocess import call
from subprocess import check_output
import random
import time
import MySQLdb



#-- MySQL command and arguments --#
mysql_cmd = os.getenv('SERVER_MYSQL_PATH')
ssl_ca = os.getenv('SERVER_SSL_CA')
ssl_cert = os.getenv('SERVER_SSL_CENT')
ssl_key = os.getenv('SERVER_SSL_KEY')
host = os.getenv('SERVER_DB_HOST')
user = os.getenv('SERVER_DB_USERNAME')
password = os.getenv('SERVER_DB_PASSWORD')
database = os.getenv('SERVER_DB_NAME')


#-- Create ssl dictionary object --#
ssl =   {
        'ca': ssl_ca,
        'key': ssl_key,
        'cert': ssl_cert
        }


#-- Gets an SQL connection to use for a DB --#
def aquireSQLConnection(db_name):

    # Connect to SQL database using login and ssl-certs
    conn = MySQLdb.connect(host=host,
                         user=user,
                         passwd=password,
                         db=db_name,
                         ssl=ssl)

    return conn


#-- Wipes all data for the reports DB --#
def wipeData(cursor):
    tables = ["reports", "rooms", "floors", "buildings"]

    for table in tables:
        cursor.execute("DELETE FROM {};".format(table))


#-- Adds a building with specified name and description --#
def addBuilding(cursor, name, desc):
    cursor.executemany("INSERT INTO buildings (name, description) VALUES (%s, %s)", [(name, desc)])


#-- Adds a floor with specified building, name and description --#
def addFloor(cursor, building_id, name, desc):
    cursor.executemany("INSERT INTO floors (buildingID, name, description) VALUES (%s, %s, %s)", [(building_id, name, desc)])


#-- Adds a room with specified floor, name and description --#
def addRoom(cursor, floor_id, name, desc):
    cursor.executemany("INSERT INTO rooms (floorID, name, description) VALUES (%s, %s, %s)", [(floor_id, name, desc)])


#-- Adds a report with specified room and report data --#
def addReport(cursor, room_id, time, devices, people, estimate):
    cursor.executemany("INSERT INTO reports (roomID, time, devices, people, estimate) VALUES (%s, %s, %s, %s, %s)", [(room_id, time, devices, people, estimate)])



#-- Adds building data from JSON to the DB, returns modified JSON with IDs --#
def createFromJSON(cursor, building):

    # Add building and save new id in JSON dict
    addBuilding(cursor, building["name"], building["description"])
    cursor.execute("SELECT * FROM buildings AS b WHERE b.name = \'{}\';".format(building["name"]))
    ans = cursor.fetchone()
    building_id = ans[0]
    building["id"] = building_id

    # For each floor, add to DB and save new id to JSON dict
    for floor in building["floors"]:
        addFloor(cursor, building_id, floor["name"], floor["description"])
        cursor.execute("SELECT * FROM floors AS f WHERE f.buildingID = {} AND f.name = \'{}\';".format(building_id, floor["name"]))
        ans = cursor.fetchone()
        floor_id = ans[1]
        floor["id"] = floor_id

        # For each room, add to DB and save new id to JSON dict
        for room in floor["rooms"]:
            addRoom(cursor, floor_id, room["name"], room["description"])
            cursor.execute("SELECT * FROM rooms AS r WHERE r.floorID = {} AND r.name = \'{}\';".format(floor_id, room["name"]))
            ans = cursor.fetchone()
            room_id = ans[1]
            room["id"] = room_id

    # Return modifed JSON dict
    return building


#-- Generates fake reports a building using the modifed JSON --#
def createReportsFromJSON(cursor, building, iters):


    for i in range(0, iters):
        for floor in building["floors"]:
            for room in floor["rooms"]:
                room_id = room["id"]
                time_n = time.time()
                devices = random.randint(0,15)
                people = random.randint(0,15)
                ans = devices + people
                addReport(cursor, room_id, time_n, devices, people, ans)


l_room = {"name": "Living room", "description": "The living room"}
m_room = {"name": "My room", "description": "My room"}
h_room = {"name": "Hallway", "description": "The hallway"}
g_floor = {"name": "Ground Floor", "description": "The ground floor", "rooms": [l_room, m_room, h_room]}
home = {"name": "Home", "description": "My home", "floors": [g_floor]}

#-- Get connection and cursor to reports DB --#
conn = aquireSQLConnection("reports")
cur = conn.cursor()
conn.begin()

#-- Wipe data on database --#
wipeData(cur)
conn.commit()

#-- Obtain new cursor --#
cur = conn.cursor()

#-- Add home --#
newb = createFromJSON(cur, home)
conn.commit()

createReportsFromJSON(cur, newb, 5)
conn.commit()

print (newb)



#
# l_rooms = [{"name": "Room 0", "description": ""},{"name": "Room 1", "description": ""},{"name": "Room 2", "description": ""},
#             {"name": "Room 3", "description": ""},{"name": "Room 4", "description": ""},{"name": "Room 5", "description": ""},
#             {"name": "Room 6", "description": ""},{"name": "Room 7", "description": ""},{"name": "Room 8", "description": ""},
#             {"name": "Room 9", "description": ""},{"name": "Room 10", "description": ""},{"name": "Room 11", "description": ""}]
#
# l_floors = [{"name": "Floor 0", "description": "", "rooms": l_rooms}, {"name": "Floor 1", "description": "", "rooms": l_rooms[:-3]},
#             {"name": "Floor 2", "description": "", "rooms": l_rooms[:-8]}, {"name": "Floor 3", "description": "", "rooms": l_rooms[:-7]},
#             {"name": "Floor 4", "description": "", "rooms": l_rooms}, {"name": "Floor 5", "description": "", "rooms": l_rooms[:-6]},
#             {"name": "Floor 6", "description": "", "rooms": l_rooms}, {"name": "Floor 7", "description": "", "rooms": l_rooms},
#             {"name": "Floor 8", "description": "", "rooms": l_rooms[:-2]}, {"name": "Floor 9", "description": "", "rooms": l_rooms},
#             {"name": "Floor 10", "description": "", "rooms": l_rooms}, {"name": "Floor 11", "description": "", "rooms": l_rooms[:-8]},
#             {"name": "Floor 12", "description": "", "rooms": l_rooms[:-7]}, {"name": "Floor 13", "description": "", "rooms": l_rooms[:-10]}]
#
# lib = {"name": "UoG Library", "description": "The University of Glagow library", "floors": l_floors}
