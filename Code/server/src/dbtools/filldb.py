import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from subprocess import call
from subprocess import check_output
import random
import time
import json
import secrets

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
    cursor.executemany("INSERT INTO rpis (roomID, name, description, auth_key) VALUES (%s, %s, %s, %s)", [(str(room_id), name, desc, secrets.token_bytes(nbytes=255))])


#-- Adds a report with specified rpi and report data --#
def addReport(cursor, rpi_id, time, devices, people):
    cursor.executemany("INSERT INTO reports (rpiID, time, devices, people) VALUES (%s, %s, %s, %s)", [(rpi_id, time, devices, people)])


#-- Adds building data from JSON to the DB, returns modified JSON with IDs --#
def createFromJSON(cursor, building):

    # Add building and save new id in JSON dict
    addBuilding(cursor, building["name"], building["description"])
    cursor.execute("SELECT id FROM buildings AS b WHERE b.name = \"{}\";".format(building["name"]))
    ans = cursor.fetchone()
    building_id = ans[0]
    building["id"] = building_id

    # For each floor, add to DB and save new id to JSON dict
    for floor in building["floors"]:
        addFloor(cursor, building_id, floor["name"], floor["description"])
        cursor.execute("SELECT id FROM floors AS f WHERE f.buildingID = {} AND f.name = \"{}\";".format(building_id, floor["name"]))
        ans = cursor.fetchone()
        floor_id = ans[0]
        floor["id"] = floor_id

        # For each room, add to DB and save new id to JSON dict
        for room in floor["rooms"]:
            addRoom(cursor, floor_id, room["name"], room["description"])
            cursor.execute("SELECT id FROM rooms AS r WHERE r.floorID = {} AND r.name = \"{}\";".format(floor_id, room["name"]))
            ans = cursor.fetchone()
            room_id = ans[0]
            room["id"] = room_id

            for rpi in room["rpis"]:
                addRPi(cursor, room_id, rpi["name"], rpi["description"])
                cursor.execute("SELECT id,auth_key FROM rpis AS r WHERE r.roomID = {} AND r.name = \"{}\";".format(room_id, rpi["name"]))
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
                    t = random.randint(1,3)
                    r = [5, 5,10,25,50]
                    devices = random.randint(0,r[t])
                    people = random.randint(0,r[t-1])
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
    cursor.execute("CREATE TABLE rpis (name varchar(255) NOT NULL, id int NOT NULL AUTO_INCREMENT, roomID int NOT NULL, description text, auth_key varchar(255) NOT NULL, PRIMARY KEY  (id), FOREIGN KEY (roomID) REFERENCES rooms(id) ON DELETE CASCADE)")
    cursor.execute("CREATE TABLE reports (id int NOT NULL AUTO_INCREMENT, rpiID int NOT NULL, time int, people float, devices float, PRIMARY KEY  (id), FOREIGN KEY (rpiID) REFERENCES rpis(id) ON DELETE CASCADE)")
    cursor.execute("CREATE TABLE estimates (id int NOT NULL AUTO_INCREMENT, roomID int NOT NULL, time int, estimate int, PRIMARY KEY  (id), FOREIGN KEY (roomID) REFERENCES rooms(id) ON DELETE CASCADE)")
    cursor.execute("CREATE TABLE readings (id int NOT NULL AUTO_INCREMENT, roomID int NOT NULL, timeS int NOT NULL, timeF int NOT NULL, reading int, PRIMARY KEY  (id), FOREIGN KEY (roomID) REFERENCES rooms(id) ON DELETE CASCADE)")

    conn.commit()

    conn = aquireSQLConnection("users")
    cursor = conn.cursor()
    conn.begin()

    #cursor.execute("CREATE TABLE users (id int NOT NULL AUTO_INCREMENT PRIMARY KEY, username varchar(255) NOT NULL UNIQUE, passhash varchar(255) NOT NULL)")

    conn.commit()




stime = 1522071000
bo720people = [23, 23, 26, 26, 18, 18, 21, 16]
bo720time = []
i = 0
last = 0
for b in bo720people:
    bo720time.append(stime + i*1800)
    i+=1
    last = stime + i*1800


stime = 1522141200
bo720people = [1, 1, 2, 5, 8, 14, 14, 20, 17, 18, 20, 20, 24]
bo720time = []
i = 0
last = 0
for b in bo720people:
    bo720time.append(stime + i*1800)
    i+=1
    last = stime + i*1800



# stime = 1522071600
# bo715people = [4, 4, 4, 4, 1, 1, 1, 1]
# bo715time = []
# i = 0
# last = 0
# for b in bo715people:
#     bo715time.append(stime + i*1800)
#     i+=1
#     last = stime + i*1800


conn = aquireSQLConnection("reports")

#-- Obtain new cursor --#
cur = conn.cursor()
cur.execute("SELECT * FROM reports WHERE reports.rpiID = 3 AND reports.time < {} AND reports.time > {} ORDER BY reports.time ASC;".format(last+3600, stime))
ans = cur.fetchall()

xx = []
xx2 = []
xy = []
xy2 = []


for an in ans:
    xx.append(an[2]-3600)
    xy.append(an[4])

cur = conn.cursor()
cur.execute("SELECT time,estimate FROM estimates WHERE estimates.roomID = 8 AND estimates.time < {} AND estimates.time > {} ORDER BY estimates.time ASC;".format(last+3600, stime))
ans = cur.fetchall()


for an in ans:
    xx2.append(an[0])
    xy2.append(an[1])

import math
import matplotlib.pyplot as plt
print (max(xx))

#plt.plot(xx, xy, label='No. of devices')
plt.plot(xx2, xy2, label="Model predictions")
plt.plot(bo720time, bo720people,  label='No. of people')
plt.legend(loc='upper left')
plt.show()
print (xx)
print (xy)


sys.exit(-1)



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
with open('../server/buildings/home.json') as data_file:
    home = json.load(data_file)
newb = createFromJSON(cur, home)
conn.commit()


#-- Add home --#
home = {}
with open('../server/buildings/example.json') as data_file:
    home = json.load(data_file)
newb = createFromJSON(cur, home)
conn.commit()

#-- Add library --#
home = {}
with open('../server/buildings/library.json') as data_file:
    home = json.load(data_file)
newb = createFromJSON(cur, home)
conn.commit()

# # Get connection and cursor to DB
conn = aquireSQLConnection("users")
cur = conn.cursor()
conn.begin()

#-- Wipe data on users database
wipeUsersData(cur)
conn.commit()

#-- Add users --#
addUser(cur, "admin", "adminpassword")
conn.commit()



conn = aquireSQLConnection("reports")
cur = conn.cursor()
conn.begin()

#-- Add some reports --#
while (True):
    print ("--")
    createReportsFromJSON(cur, newb, 10)
    conn.commit()
    time.sleep(10)
