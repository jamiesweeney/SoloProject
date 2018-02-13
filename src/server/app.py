import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flask import Flask
from subprocess import call
from subprocess import check_output
import random
from flask import request,  render_template, json

app = Flask(__name__)


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


#-- Web pages --#
@app.route("/webapp/home")
def wp_index():
    return render_template('/html/home.html')

@app.route("/webapp/building/<int:building_id>")
def wp_building(building_id):
    return render_template('/html/building.html', building_id=building_id)

@app.route("/webapp/floor/<int:floor_id>")
def wp_floor(floor_id):
    return render_template('/html/floor.html')

@app.route("/webapp/room/<int:room_id>")
def wp_room(room_id):
    return render_template('/html/room.html')


#-- Get Requests --#
# Returns all the buildings
@app.route("/api/v1/buildings/get-all")
def getAllBuildings():
    cmd = ("\"SELECT * FROM buildings;\"")
    db_response = send_command(cmd)

    buildings = []
    for building in db_response:
        info = {"building_id": building[0], "building_name": building[1], "building_desc": building[2]}
        buildings.append(info)
    data = {}
    data = {"buildings": buildings}

    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response

# Returns the information for one building
@app.route("/api/v1/buildings/get/<int:building_id>")
def getBuilding(building_id):
    cmd = ("\"SELECT * FROM floors AS f WHERE f.buildingID = {}\";").format(str(building_id))
    db_response = send_command(cmd)

    floors = []
    for floor in db_response:
        info = {"building_id": floor[0], "floor_id": floor[1], "floor_name": floor[2], "floor_desc" : floor[3]}
        floors.append(info)
    data = {"floors": floors}

    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response

# Returns the information for one floor
@app.route("/api/v1/floors/get/<int:floor_id>")
def getFloor(floor_id):
    cmd = ("\"SELECT * FROM rooms AS r WHERE r.floorID = {}\";").format(str(floor_id))
    db_response = send_command(cmd)

    rooms = []
    for room in db_response:
        info = {"floor_id": room[0], "room_id": room[1], "room_name": room[2], "room_desc" : room[3]}
        rooms.append(info)
    data = {"rooms": rooms}

    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response

# Returns the information for one room
@app.route("/api/v1/rooms/get/<int:room_id>")
def getRoom(room_id):
    cmd = ("\"SELECT * FROM reports AS r WHERE r.roomID = {} ORDER BY r.time DESC LIMIT 20\";").format(str(room_id))
    db_response = send_command(cmd)

    reports = []
    for report in db_response:
        info = {"room_id": report[0], "report_id": report[1], "time": report[2], "devices" : report[3], "people" : report[4], "estimate" : report[5]}
        reports.append(info)

    data = {"reports": reports}

    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response

# Returns current prediction for one room
@app.route("/api/v1/rooms/get_estimate/<int:room_id>")
def getRoomEstimate(room_id):
    cmd = ("\"SELECT * FROM reports AS r WHERE r.roomID = {} ORDER BY r.time DESC LIMIT 1\";").format(str(room_id))
    db_response = send_command(cmd)

    report = db_response[0]
    info = {"room_id": report[0], "time": report[2], "estimate" : report[5]}

    data = {"report": info}

    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response


#-- Pi Requests --#
# Accepts data from a pi and adds changes to the database
@app.route("/api/v1/pi-reports/add", methods = ['POST'])
def addReport():
    content = request.get_json()

    # Verify identity
    auth = content['auth']
    if (magic_authentication(auth) == False):
        return "NOT AUTHORIZED"

    # Get data
    room_id = content['roomID']
    time_n = content['time']
    devices = content['devices']
    people = content['people']

    # Feed data to linear Regression alg
    ans =  magic_algorithm(room_id, time_n, devices, people)

    # Put output into database
    cmd = ("\"INSERT INTO reports (roomID, time, devices, people, estimate) VALUES ({}, {}, {}, {}, {})\";").format(room_id,time_n, devices, people, ans)
    response = send_command(cmd)
    return "OK"


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
def magic_algorithm(room_id, time_n, devices, people):
    return (random.randint(0,100))


if __name__ == "__main__":
    app.run(host='0.0.0.0')
