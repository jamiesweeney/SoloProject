import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from subprocess import call
from subprocess import check_output
import random
import time

#-- MySQL command and arguments --#
mysql_cmd = os.getenv('SERVER_MYSQL_PATH')
ssl_ca = os.getenv('SERVER_SSL_CA')
ssl_cert = os.getenv('SERVER_SSL_CENT')
ssl_key = os.getenv('SERVER_SSL_KEY')
host = os.getenv('SERVER_DB_HOST')
user = os.getenv('SERVER_DB_USERNAME')
password = os.getenv('SERVER_DB_PASSWORD')
database = os.getenv('SERVER_DB_NAME')

# Base cmd, can be exteneded with a SQL command using the '-e' input var
base_cmd = "\"{}\" --ssl-ca=\"{}\" --ssl-cert=\"{}\" --ssl-key=\"{}\" --host=\"{}\" --user=\"{}\" --password=\"{}\" --database=\"{}\"".format(mysql_cmd, ssl_ca, ssl_cert, ssl_key, host, user, password, database)

def send_command(cmd):
    call_str = "{} -e {}".format(base_cmd, cmd)
    ans = check_output(call_str)    # Get output
    ans = ans.decode("utf-8")       # Decode from bytes
    ans = ans.replace('\r','')      # Format a little
    ans = ans.split("\n")[1:]       # Remove header
    for i in range(0, len(ans)):    # Split cells in row to list format
        ans[i] = ans[i].split('\t')
    ans = ans[:-1]
    return ans

def wipeData():
    tables = ["reports", "rooms", "floors", "buildings"]

    for table in tables:
        cmd = ("\"DELETE FROM {}\";").format(table)
        call_str = "{} -e {}".format(base_cmd, cmd)
        ans = check_output(call_str)

def addBuilding(name, desc):

    cmd = ("\"INSERT INTO buildings (name, description) VALUES ('{}', '{}')\";").format(name, desc)
    call_str = "{} -e {}".format(base_cmd, cmd)
    ans = check_output(call_str)    # Get output

def addFloor(building, name, desc):
    cmd = ("\"INSERT INTO floors (buildingID, name, description) VALUES ({}, '{}', '{}')\";").format(building, name, desc)
    call_str = "{} -e {}".format(base_cmd, cmd)
    ans = check_output(call_str)    # Get output

def addRoom(floor, name, desc):
    cmd = ("\"INSERT INTO rooms (floorID, name, description) VALUES ({}, '{}', '{}')\";").format(floor, name, desc)
    call_str = "{} -e {}".format(base_cmd, cmd)
    ans = check_output(call_str)    # Get output

def createTestData():
    rooms = []

    # Make a random number of buildings
    x = random.randint(2,5)
    for i in range(1,x):
        addBuilding("Test Building" + str(i), "-")
        cmd = ("\"SELECT * FROM buildings AS b WHERE b.name = \'{}\'\";").format("Test Building" + str(i))
        building_id = send_command(cmd)[0][0]
        print (building_id)
        y = random.randint(3, 5)
        for j in range(1,y):
            addFloor(building_id,"Test Floor" + str(j), "-")
            cmd = ("\"SELECT * FROM floors AS f WHERE f.buildingID = {} AND f.name = \'{}\'\";").format(building_id, "Test Floor" + str(j))
            floor_id = send_command(cmd)[0][1]
            print (floor_id)
            z = random.randint(3, 5)
            for k in range(1,z):
                addRoom(floor_id,"Test Room" + str(k), "-")
                cmd = ("\"SELECT * FROM rooms AS r WHERE r.floorID = {} AND r.name = \'{}\'\";").format(floor_id, "Test Room" + str(k))
                room_id = send_command(cmd)[0][1]
                print (room_id)
                rooms.append(room_id)

    return rooms

def createTestReports(rooms, iters):
    for i in range(1, iters):
        for room in rooms:
            time_n = time.time()
            devices = random.randint(0,15)
            people = random.randint(0,15)
            ans = devices + people

            cmd = ("\"INSERT INTO reports (roomID, time, devices, people, estimate) VALUES ({}, {}, {}, {}, {})\";").format(room, time_n, devices, people, ans)
            response = send_command(cmd)
        time.sleep(30)


wipeData()
rooms = createTestData()
print (rooms)
createTestReports(rooms, 5)
