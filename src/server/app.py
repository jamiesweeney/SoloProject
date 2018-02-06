import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flask import Flask
from subprocess import call
from subprocess import check_output
import config
import random

app = Flask(__name__)


# My SQL command and arguments
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


#-- Get Requests --#
# Returns all the buildings
@app.route("/api/v1/buildings/get-all")
def getAllBuildings():
    cmd = ("\"SELECT * FROM buildings;\"")
    response = send_command(cmd)
    return str(response)

# Returns the information for one building
@app.route("/api/v1/buildings/get/<int:building_id>")
def getBuilding(building_id):
    cmd = ("\"SELECT * FROM floors AS f WHERE f.buildingID = {}\";").format(str(building_id))
    response = send_command(cmd)
    return str(response)


# Returns the information for one floor
@app.route("/api/v1/floors/get/<int:floor_id>")
def getFloor(floor_id):
    cmd = ("\"SELECT * FROM rooms AS r WHERE r.floorID = {}\";").format(str(floor_id))
    response = send_command(cmd)
    return str(response)

# Returns the information for one room
@app.route("/api/v1/rooms/get/<int:room_id>")
def getRoom(room_id):
    cmd = ("\"SELECT * FROM reports AS r WHERE r.roomID = {} ORDER BY r.time DESC LIMIT 20\";").format(str(room_id))
    response = send_command(cmd)
    return str(response)


#-- Pi Requests --#
# Accepts data from a pi and adds changes to the database
@app.route("/api/v1/pi-reports/add", methods = ['POST'])
def addReport():
    content = request.get_json()

    # Verify identity
    if (magic_authentication(content) == False):
        return "NOT AUTHORIZED"

    # Feed data to linear Regression alg
    ans =  magic_algorithm(content)

    # Put output into database
    cmd = ("\"INSERT INTO reports (roomID, time, devices, people, estimate) VALUES ()\";").format(str(room_id))
    response = send_command(cmd)
    return response


#-- Authentication --#
# Authenticates the RPi requests for data changes
def magic_authentication(request):
    return True


#-- Database Management --#
# Sends a command to the database
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


#-- Linear Regression --#
# Takes RPi output data and returns a guess of room occupancy based on linear reg alg.
def magic_algorithm(input):
    return (random.randint(0,100))


if __name__ == "__main__":
    app.run(host='0.0.0.0', ssl_context='adhoc')
