import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from subprocess import call
from subprocess import check_output
import random
import time
import json
import MySQLdb
from passlib.hash import sha256_crypt



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
def wipeReportData(cursor):
    tables = ["reports", "rooms", "floors", "buildings"]

    for table in tables:
        cursor.execute("DELETE FROM {};".format(table))


#-- Wipes all data for the users DB --#
def wipeUsersData(cursor):
    cursor.execute("DELETE FROM users;")


#-- Adds a building with specified name and description --#
def addBuilding(cursor, name, desc):
    cursor.executemany("INSERT INTO buildings (name, description) VALUES (%s, %s)", [(name, desc)])


#-- Adds a floor with specified building, name and description --#
def addFloor(cursor, building_id, name, desc):
    cursor.executemany("INSERT INTO floors (buildingID, name, description) VALUES (%s, %s, %s)", [(building_id, name, desc)])


#-- Adds a room with specified floor, name and description --#
def addRoom(cursor, floor_id, name, desc):
    cursor.executemany("INSERT INTO rooms (floorID, name, description) VALUES (%s, %s, %s)", [(floor_id, name, desc)])


def addRPi(cursor, room_id, name, desc):
    cursor.executemany("INSERT INTO rpis (roomID, name, description) VALUES (%s, %s, %s)", [(room_id, name, desc)])


#-- Adds a report with specified rpi and report data --#
def addReport(cursor, rpi_id, time, devices, people):
    cursor.executemany("INSERT INTO reports (rpiID, time, devices, people) VALUES (%s, %s, %s, %s)", [(rpi_id, time, devices, people)])


#-- Adds building data from JSON to the DB, returns modified JSON with IDs --#
def createFromJSON(cursor, building):

    # Add building and save new id in JSON dict
    addBuilding(cursor, building["name"], building["description"])
    cursor.execute("SELECT id FROM buildings AS b WHERE b.name = \'{}\';".format(building["name"]))
    ans = cursor.fetchone()
    building_id = ans[0]
    building["id"] = building_id

    # For each floor, add to DB and save new id to JSON dict
    for floor in building["floors"]:
        addFloor(cursor, building_id, floor["name"], floor["description"])
        cursor.execute("SELECT id FROM floors AS f WHERE f.buildingID = {} AND f.name = \'{}\';".format(building_id, floor["name"]))
        ans = cursor.fetchone()
        floor_id = ans[0]
        floor["id"] = floor_id

        # For each room, add to DB and save new id to JSON dict
        for room in floor["rooms"]:
            addRoom(cursor, floor_id, room["name"], room["description"])
            cursor.execute("SELECT id FROM rooms AS r WHERE r.floorID = {} AND r.name = \'{}\';".format(floor_id, room["name"]))
            ans = cursor.fetchone()
            room_id = ans[0]
            room["id"] = room_id

            for rpi in room["rpis"]:
                addRPi(cursor, room_id, rpi["name"], rpi["description"])
                cursor.execute("SELECT id,auth_key FROM rpis AS r WHERE r.roomID = {} AND r.name = \'{}\';".format(room_id, rpi["name"]))
                ans = cursor.fetchone()
                rpi_id = ans[0]
                rpi_auth = ans[1]
                rpi["id"] = rpi_id
                rpi["auth_key"] = rpi_auth



    # Return modifed JSON dict
    return building


#-- Generates fake reports a building using the modifed JSON --#
def createReportsFromJSON(cursor, building, iters):
    for i in range(0, iters):
        for floor in building["floors"]:
            for room in floor["rooms"]:
                for rpi in room["rpis"]:

                    rpi_id = rpi["id"]
                    rpi_auth = rpi["auth_key"]

                    time_n = time.time()
                    devices = random.randint(0,15)
                    people = random.randint(0,15)
                    ans = devices + people
                    addReport(cursor, rpi_id, time_n, devices, people)


#-- Adds a user to the user database --#
def addUser(cursor, username, password):
    new_password =  sha256_crypt.encrypt(password)
    print (sha256_crypt.verify(password, new_password))
    print (len(new_password))
    cursor.executemany("INSERT INTO users (username, passhash) VALUES (%s, %s)", [(username, new_password)])







def scrapTables(cursor):
    cursor.execute("show tables;")
    ans = cursor.fetchall()[::-1]
    print ((ans))
    for t in ans:
        try:
            cursor.execute("drop table {};".format(t[0]))
        except:
            pass


def setupTables():

    conn = aquireSQLConnection("reports")
    cursor = conn.cursor()
    conn.begin()

    cursor.execute("CREATE TABLE buildings (name varchar(255) NOT NULL, id int NOT NULL AUTO_INCREMENT PRIMARY KEY, description text)")
    cursor.execute("CREATE TABLE floors (name varchar(255) NOT NULL, id int NOT NULL AUTO_INCREMENT, buildingID int NOT NULL, description text, PRIMARY KEY  (id), FOREIGN KEY (buildingID) REFERENCES buildings(id) ON DELETE CASCADE)")
    cursor.execute("CREATE TABLE rooms (name varchar(255) NOT NULL, id int NOT NULL AUTO_INCREMENT, floorID int NOT NULL, description text, PRIMARY KEY  (id), FOREIGN KEY (floorID) REFERENCES floors(id) ON DELETE CASCADE)")
    cursor.execute("CREATE TABLE rpis (name varchar(255) NOT NULL, id int NOT NULL AUTO_INCREMENT, roomID int NOT NULL, description text, auth_key varchar(255), PRIMARY KEY  (id), FOREIGN KEY (roomID) REFERENCES rooms(id) ON DELETE CASCADE)")
    cursor.execute("CREATE TABLE reports (id int NOT NULL AUTO_INCREMENT, rpiID int NOT NULL, time int, people float, devices float, PRIMARY KEY  (id), FOREIGN KEY (rpiID) REFERENCES rpis(id) ON DELETE CASCADE)")
    cursor.execute("CREATE TABLE estimates (id int NOT NULL AUTO_INCREMENT, roomID int NOT NULL, time int, estimate int, PRIMARY KEY  (id), FOREIGN KEY (roomID) REFERENCES rooms(id) ON DELETE CASCADE)")

    conn.commit()








# #-- Get connection and cursor to reports DB --#


#-- Wipe data on reports database --#


#wipeReportData(cur)
#conn.commit()

conn = aquireSQLConnection("reports")

#-- Obtain new cursor --#
cur = conn.cursor()
scrapTables(cur)
scrapTables(cur)
scrapTables(cur)
scrapTables(cur)
scrapTables(cur)
scrapTables(cur)
setupTables()

#-- Add home --#
home = {}
with open('home.json') as data_file:
    home = json.load(data_file)
newb = createFromJSON(cur, home)
conn.commit()

#-- Add some reports --#
createReportsFromJSON(cur, newb, 1)
conn.commit()



# # Get connection and cursor to DB
# conn = aquireSQLConnection("users")
# cur = conn.cursor()
# conn.begin()

#-- Wipe data on users database
# wipeUsersData(cur)
# conn.commit()

#-- Add users --#
# addUser(cur, "Jamie", "jamiepassword")
#addUser(cur, "admin", "adminpassword")
#addUser(cur, "Jeremy", "jeremypassword")
#conn.commit()
#
# # Get user data from database
# cur.execute("SELECT userID, username FROM users AS u WHERE u.username = \'{}\';".format("Jamie"))
# ans = cur.fetchone()
# user_id = ans[0]
# username = ans[1]
# print (user_id)
# print (username)
#
# cur.execute("SELECT * FROM users;")
# print (cur.fetchall())
#
