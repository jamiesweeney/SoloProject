import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flask import Flask
from subprocess import call
from subprocess import check_output
import random
import secrets
from flask import request,  render_template, json, redirect, Response, url_for
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, confirm_login
from urllib.parse import urlparse, urljoin
import MySQLdb
from passlib.hash import sha256_crypt
import json
from sklearn import linear_model
import pickle
import numpy as np
import time
import glob


#-- Flask app config --#
app = Flask(__name__)
app.config.update(SECRET_KEY = os.getenv('SERVER_SECRET'))


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


#-- Create user manager objects --#
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "wp_login"


#-- Public Web pages --#

# Index page - redirects to home
@app.route("/")
def wp_index():
    return redirect(url_for("wp_home", code=302))

# Home page - shows all buildings and links
@app.route("/webapp/home")
def wp_home():
    return render_template('/html/home.html')

# Building page - shows a building floor by floor with estimations for each floor
@app.route("/webapp/building/<int:building_id>")
def wp_building(building_id):
    return render_template('/html/building.html', building_id=building_id)

# Floor page - shows a floor room by room with estimations for each floor
@app.route("/webapp/floor/<int:floor_id>")
def wp_floor(floor_id):
    return render_template('/html/floor.html')

# Room page - shows nothing just now
# TODO - Implement this page
@app.route("/webapp/room/<int:room_id>")
def wp_room(room_id):
    return render_template('/html/room.html')

# Login page - allows the user to log in, accepts 'next' param or redirects to home
@app.route("/webapp/login", methods=["GET", "POST"])
def wp_login():

    # If recieved a POST request (logging in)
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # If user login details are valid
        if (doLogin(username, password)):

            # Get connection and cursor to DB
            conn = aquireSQLConnection("users")
            cur = conn.cursor()

            # Get user data from database
            cur.execute("SELECT userID FROM users AS u WHERE u.username = \'{}\';".format(username))
            ans = cur.fetchone()

            # Create user object
            usr = User(username,ans[0])

            # Log the user in
            login_user(usr)

            # Get the next param and redirect there
            # ONLY IF THE URL IS SAFE
            next = request.args.get('next')
            if is_safe_url(next):
                return redirect(next)

            # No safe next param - just redirect to the home page.
            return redirect(url_for("wp_home"))

        else:

            # If details are not valid, then try again
            return redirect(url_for("wp_login"))

    # If not a POST request serve the login page
    else:
        return render_template("/html/login.html")


#-- Admin Web pages --#

# Admin page - all the admin tools
@app.route("/webapp/admin")
@login_required     # Important
def wp_admin():

    return render_template('/html/admin.html')

# Logout page - allows current user to log out, redirects to home
@app.route("/webapp/logout")
@login_required     # Important
def wp_logout():
    logout_user()
    return redirect(url_for("wp_home"))


#-- Public get requests --#
# Returns all the buildings
@app.route("/api/v1/buildings/get-all")
def getAllBuildings():

    # Get connection and cursor to DB
    conn = aquireSQLConnection("reports")
    cur = conn.cursor()

    # Get all buildings
    cur.execute("SELECT id,name,description FROM buildings;")
    ans = cur.fetchall()

    # Create buildings JSON object
    buildings = []
    for building in ans:
        info = {"building_id": building[0], "building_name": building[1], "building_desc": building[2]}
        buildings.append(info)
    data = {"buildings": buildings}

    # Serve response
    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response

# Returns the information for one building
@app.route("/api/v1/buildings/get/<int:building_id>")
def getBuilding(building_id):

    # Get connection and cursor to DB
    conn = aquireSQLConnection("reports")
    cur = conn.cursor()

    # Get building data
    cur.execute("SELECT buildingID,id,name,description FROM floors AS f WHERE f.buildingID = {};".format(building_id))
    ans = cur.fetchall()

    # Create buildings JSON object
    floors = []
    for floor in ans:
        info = {"building_id": floor[0], "floor_id": floor[1], "floor_name": floor[2], "floor_desc" : floor[3]}
        floors.append(info)
    data = {"floors": floors}

    # Serve response
    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response

# Returns the information for one floor
@app.route("/api/v1/floors/get/<int:floor_id>")
def getFloor(floor_id):

    # Get connection and cursor to DB
    conn = aquireSQLConnection("reports")
    cur = conn.cursor()

    # Get room data for rooms on floor
    cur.execute("SELECT floorID, id, name, description FROM rooms AS r WHERE r.floorID = {};".format(floor_id))
    ans = cur.fetchall()

    # Create floor JSON object
    rooms = []
    for room in ans:
        info = {"floor_id": room[0], "room_id": room[1], "room_name": room[2], "room_desc" : room[3]}
        rooms.append(info)
    data = {"rooms": rooms}

    # Server response
    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response

# Returns the information for one room
@app.route("/api/v1/rooms/get/<int:room_id>")
def getRoom(room_id):

    # Get connection and cursor to DB
    conn = aquireSQLConnection("reports")
    cur = conn.cursor()

    # Get
    cur.execute("SELECT * FROM estimates AS r WHERE r.roomID = {} ORDER BY r.time DESC LIMIT 20;".format(room_id))
    ans = cur.fetchall()

    estimates = []
    for estimate in ans:
        info = {"room_id": room_id, "time": estimate[2], "estimate" : estimate[3]}
        estimates.append(info)

    data = {"estimates": estimates}

    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response

# Returns current prediction for one room
@app.route("/api/v1/rooms/get_estimate/<int:room_id>")
def getRoomEstimate(room_id):

    # Get connection and cursor to DB
    conn = aquireSQLConnection("reports")
    cur = conn.cursor()

    cur.execute("SELECT * FROM estimates AS r WHERE r.roomID = {} ORDER BY r.time DESC LIMIT 1;".format(room_id))
    ans = cur.fetchone()

    if (ans != None):
        info = {"room_id": room_id, "time": ans[2], "estimate" : ans[3]}
        data = {"estimate": info}
    else:
        data = {"estimate": None}
    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response


#-- Admin get requests --#
# Returns admin data for one building
@app.route("/api/v1/buildings/admin-get/<int:building_id>")
@login_required     # Important
def adminGetBuilding(building_id):

    # Get connection and cursor to DB
    conn = aquireSQLConnection("reports")
    cur = conn.cursor()

    # Get building data
    cur.execute("SELECT name, description FROM buildings AS b WHERE b.id = {};".format(building_id))
    ans = cur.fetchall()

    # Init building JSON object
    building = {"id":building_id, "name": ans[0][0], "description": ans[0][1], "floors":[]}

    # Get each floor
    cur.execute("SELECT name, id, description FROM floors AS f WHERE f.buildingID = {};".format(building_id))
    ans = cur.fetchall()

    # For each floor, init floor object
    for floor in ans:
        floor_id = floor[1]
        info = {"building_id": building_id, "floor_id": floor[1], "floor_name": floor[0], "floor_desc" : floor[2], "rooms":[]}

        # Get each room
        cur.execute("SELECT name, id, description FROM rooms AS r WHERE r.floorID = {};".format(floor_id))
        rooms = cur.fetchall()

        # For each room, init room object
        for room in rooms:
            room_id = room[1]
            room_info = {"building_id": building_id, "floor_id": floor_id, "room_id": room[1], "room_name": room[0], "room_desc" : room[2], "rpis":[]}

            # Get each rpi
            cur.execute("SELECT name, id, description, auth_key FROM rpis AS r WHERE r.roomID = {};".format(room_id))
            rpis = cur.fetchall()

            # For each rpi, init rpi object
            for rpi in rpis:
                rpi_info = {"building_id": building_id, "floor_id": floor_id, "room_id": room_id, "rpi_id": rpi[1], "rpi_name": rpi[0], "rpi_desc": rpi[2], "auth_key": rpi[3]}

                cur.execute("SELECT time FROM reports AS r WHERE r.rpiID = {} ORDER BY r.time DESC LIMIT 1;".format(rpi[1]))
                ans = cur.fetchone()
                if (ans != None):
                    rpi_info["last_report"] = ans[0]
                else:
                    rpi_info["last_report"] = None

                # Add rpi to room
                room_info["rpis"].append(rpi_info)
            # Add room to floor
            info["rooms"].append(room_info)
        # Add floor to building
        building["floors"].append(info)

    # Serve the response
    return app.response_class(
        response=json.dumps(building),
        status=200,
        mimetype='application/json'
    )

# Returns admin data for users
@app.route("/api/v1/users/admin-get-all")
@login_required     # Important
def adminGetUsers():

    # Get connection and cursor to DB
    conn = aquireSQLConnection("users")
    cur = conn.cursor()

    # Gets user data
    cur.execute("SELECT userID, username FROM users;".format())
    ans = cur.fetchall()

    # Server JSON response
    ans = {"users":ans}
    response = app.response_class(
        response=json.dumps(ans),
        status=200,
        mimetype='application/json'
    )
    return response

# Returns admin data for users
@app.route("/api/v1/do-estimates")
@login_required     # Important
def adminDoEstimates():
    makePredictions()
    return "OK"


#-- Admin POST requests --#
# Request for adding a new building
@app.route("/api/v1/buildings/admin-add", methods=['POST'])
@login_required     # Important
def adminAddBuilding():

    # Get building data from JSON
    content = json.loads(str(request.get_data().decode("utf-8")))

    # Get connection and cursor to DB
    conn = aquireSQLConnection("reports")
    cur = conn.cursor()

    # Add building to database
    cur.executemany("INSERT INTO buildings (name, description) VALUES (%s, %s)", [(content["name"], content["description"])])
    ans = cur.fetchall()
    conn.commit()

    # Serve success response
    return "OK"

# Request for deleting a building
@app.route("/api/v1/buildings/admin-delete", methods=['POST'])
@login_required     # Important
def adminDelBuilding():

    # Get building data from JSON
    content = json.loads(str(request.get_data().decode("utf-8")))

    # Get connection and cursor to DB
    conn = aquireSQLConnection("reports")
    cur = conn.cursor()

    # Delete building from database
    cur.execute("DELETE FROM buildings WHERE id = {};".format(content["id"]))
    ans = cur.fetchall()
    conn.commit()

    # Serve sucess response
    return "OK"

# Request for adding a new floor
@app.route("/api/v1/floors/admin-add", methods=['POST'])
@login_required     # Important
def adminAddFloor():

    # Get floor data from JSON
    content = json.loads(str(request.get_data().decode("utf-8")))

    # Get connection and cursor to DB
    conn = aquireSQLConnection("reports")
    cur = conn.cursor()

    # Add floor to database
    cur.executemany("INSERT INTO floors (buildingID, name, description) VALUES (%s, %s, %s)", [(str(content["building_id"]), content["name"], content["description"])])
    ans = cur.fetchall()
    conn.commit()

    # Serve sucess response
    return "OK"

# Request for deleting a floor
@app.route("/api/v1/floors/admin-delete", methods=['POST'])
@login_required     # Important
def adminDelFloor():

    # Get floor data from JSON
    content = json.loads(str(request.get_data().decode("utf-8")))

    # Get connection and cursor to DB
    conn = aquireSQLConnection("reports")
    cur = conn.cursor()

    # Remove floor from database
    cur.execute("DELETE FROM floors WHERE id = {};".format(content["id"]))
    ans = cur.fetchall()
    conn.commit()

    # Serve sucess response
    return "OK"

# Request for adding a new room
@app.route("/api/v1/rooms/admin-add", methods=['POST'])
@login_required     # Important
def adminAddRoom():

    # Get room data from JSON
    content = json.loads(str(request.get_data().decode("utf-8")))

    # Get connection and cursor to DB
    conn = aquireSQLConnection("reports")
    cur = conn.cursor()

    # Add room to database
    cur.executemany("INSERT INTO rooms (floorID, name, description) VALUES (%s, %s, %s)", [(str(content["floor_id"]), content["name"], content["description"])])
    ans = cur.fetchall()
    conn.commit()

    # Serve sucess response
    return "OK"

# Request for deleting a room
@app.route("/api/v1/rooms/admin-delete", methods=['POST'])
@login_required     # Important
def adminDelRoom():

    # Get room data from JSON
    content = json.loads(str(request.get_data().decode("utf-8")))

    # Get connection and cursor to DB
    conn = aquireSQLConnection("reports")
    cur = conn.cursor()

    # Delete room from database
    cur.execute("DELETE FROM rooms WHERE id = {};".format(content["id"]))
    ans = cur.fetchall()
    conn.commit()

    # Serve sucess response
    return "OK"

# Request for adding a new rpi
@app.route("/api/v1/rpis/admin-add", methods=['POST'])
@login_required     # Important
def adminAddRpi():

    # Get rpi data from JSON
    content = json.loads(str(request.get_data().decode("utf-8")))

    # Get connection and cursor to DB
    conn = aquireSQLConnection("reports")
    cur = conn.cursor()

    # Generate a secure key of size 255 bytes for authentication
    content["auth_key"] = secrets.token_bytes(nbytes=255)

    # Add rpi to database
    cur.executemany("INSERT INTO rpis (roomID, name, description, auth_key) VALUES (%s, %s, %s, %s)", [(str(content["room_id"]), content["name"], content["description"], content["auth_key"])])
    ans = cur.fetchall()
    conn.commit()

    # Serve success response
    return "OK"

# Request for deleting a rpi
@app.route("/api/v1/rpis/admin-delete", methods=['POST'])
@login_required     # Important
def adminDelRpis():

    # Get rpi data from JSON
    content = json.loads(str(request.get_data().decode("utf-8")))

    # Get connection and cursor to DB
    conn = aquireSQLConnection("reports")
    cur = conn.cursor()

    # Remove rpu from database
    cur.execute("DELETE FROM rpis WHERE id = {};".format(content["id"]))
    ans = cur.fetchall()
    conn.commit()

    # Serve sucess response
    return "OK"

# Request for adding a new user
@app.route("/api/v1/users/admin-add", methods=['POST'])
@login_required     # Important
def adminAddUsers():

    # Get user data from JSON
    content = json.loads(str(request.get_data().decode("utf-8")))

    # Get connection and cursor to DB
    conn = aquireSQLConnection("users")
    cur = conn.cursor()

    # Add user to database
    cur.executemany("INSERT INTO users (username, passhash) VALUES ( %s, %s)", [(content["username"],  sha256_crypt.encrypt(content["password"]))])
    ans = cur.fetchall()
    conn.commit()

    # Server success response
    return "OK"

# Request for deleting a user
@app.route("/api/v1/users/admin-delete", methods=['POST'])
@login_required     # Important
def adminDelUsers():

    # Get user data from JSON
    content = json.loads(str(request.get_data().decode("utf-8")))

    # Get connection and cursor to DB
    conn = aquireSQLConnection("users")
    cur = conn.cursor()

    # Delete user to database
    cur.execute("DELETE FROM users WHERE userID = {};".format(content["id"]))
    ans = cur.fetchall()
    conn.commit()

    # Return sucess response
    return "OK"

# Request for adding a room reading
@app.route("/api/v1/readings/admin-add", methods=['POST'])
@login_required     # Important
def adminAddReadings():
    print ("--Adding a reading")

    # Get user data from JSON
    content = json.loads(str(request.get_data().decode("utf-8")))

    # Get connection and cursor to DB
    conn = aquireSQLConnection("reports")
    cur = conn.cursor()

    # Add reading to database
    print (content)
    print ("///////////////////////////////")

    cur.executemany("INSERT INTO readings (roomID, timeS, timeF, reading) VALUES (%s, %s, %s, %s)", [(content["room"],content["stime"],content["etime"],content["value"])])
    ans = cur.fetchall()
    conn.commit()

    generateTrainingData(content)
    # Server success response
    return "OK"


#-- Pi requests --#
# Accepts data from a pi and adds changes to the database
@app.route("/api/v1/pi-reports/add", methods = ['POST'])
def addReport():

    # Get report data from JSON
    content = request.get_json()

    # Get authentication data
    auth = content['auth_key']
    rpi_id = content['rpi_id']

    # Get connection and cursor to DB
    conn  = aquireSQLConnection("reports")
    cur = conn.cursor()

    # Verify auth data
    cur.execute("SELECT auth_key from rpis as r WHERE r.id = {}").format(rpi_id)
    ans = cur.fetchone()

    # If invalid, serve unauthorized response
    if (ans[0] != auth):
        return "AUTH KEY INVALID"

    # Else, get report data
    time_n = content['time']
    devices = content['devices']
    people = content['people']

    # Add report data to database
    cursor.executemany("INSERT INTO reports (rpiID, time_n, devices, people) VALUES (%s, %s, %s, %s, %s)", [(rpi_id, time_n, devices, people)])
    ans = cur.fetchall()
    conn.commit()

    # Serve sucess response
    return "OK"


#-- User login functions / classes --#
# Authenticates users for admin access
def doLogin(username, password):

    if (username == None or password == None):
        return False

    # Get connection and cursor to DB
    conn = aquireSQLConnection("users")
    cur = conn.cursor()

    cur.execute("SELECT passhash  FROM users AS u WHERE u.username = \'{}\';".format(username))
    ans = cur.fetchone()
    if (ans != None):
        return sha256_crypt.verify(password, ans[0])
    else:
        return False

# User model
class User(UserMixin):

    user_dictionary = {}

    def __init__(self, name, id, active=True):
        self.name = name
        self.id = id
        self.active = active
        self.user_dictionary[str(id)] = self

    def is_active(self):
        return True

    def is_anonymous(self):
        return True

    def is_authenticated(self):
        return True

    def get_id(self):
        return str(self.id).encode("utf-8").decode("utf-8")

    @classmethod
    def get(self, user_id):
        user_id = str(user_id)
        if (user_id in self.user_dictionary):
            return self.user_dictionary[user_id]
        return None

# Loads a User object
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


#--  URL management --#
# Checks if a redirect url is safe to redirect to
def is_safe_url(next):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, next))
    return test_url.scheme in ('https') and \
           ref_url.netloc == test_url.netloc and \
           next != None


#-- Database management --#
# Gets an SQL connection to use for a DB
def aquireSQLConnection(db_name):

    if (app.config["TESTING"]):
        db_name = "tesing" + db_name

    # Connect to SQL database using login and ssl-certs
    conn = MySQLdb.connect(host=host,
                         user=user,
                         passwd=password,
                         db=db_name,
                         ssl=ssl)
    return conn




def deleteTables():

    # Get connection and cursor to DB
    conn = aquireSQLConnection("reports")
    cursor = conn.cursor()

    done = False
    while not done:
        done = True
        cursor.execute("show tables;")
        ans = cursor.fetchall()[::-1]
        for t in ans:
            try:
                cursor.execute("drop table {};".format(t[0]))
            except:
                done = False
    conn.commit()


def createTables():

    # Get cursor for report database
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



# Adds building data from JSON to the DB, returns modified JSON with IDs
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

def restoreFromFile():
    for filename in glob.iglob('../buildings/*.json'):
         with open(filename) as data_file:
             build = json.load(data_file)
         newb = createFromJSON(cur, build)
         conn.commit()







#-- Linear regression --#
# Takes RPi output data and returns a guess of room occupancy based on linear reg alg.

def generateTrainingData(reading):
    print ("--Generating test data")

    # Get all rpis in room
    conn = aquireSQLConnection("reports")
    cur = conn.cursor()
    cur.execute("SELECT id FROM rpis AS r WHERE r.roomID = {};".format(int(reading['room'])))
    ans = cur.fetchall()

    print ("---------------------------------------")
    print (ans)

    # Get all reports from rpis
    reports = []
    for rpi in ans[0]:
        cur = conn.cursor()
        print ("SELECT * FROM reports AS r WHERE r.rpiID = {} AND r.time > {} AND r.time < {};".format(rpi, reading["stime"], reading["etime"]))
        cur.execute("SELECT * FROM reports AS r WHERE r.rpiID = {} AND r.time > {} AND r.time < {};".format(rpi, reading["stime"], reading["etime"]))
        reps = cur.fetchall()
        reports.append(reps)

    # Generate test data
    data = {}
    data["value"] = reading["value"]
    data["room"] = reading["room"]
    data["reports"] = reports

    applyTrainingData(data)

def applyTrainingData(data):
    print ("--Applying test data")
    print (data)

    value = data["value"]
    reports = data["reports"]

    if reports == [()]:
        print ("--No reports to use")
        conn = aquireSQLConnection("reports")
        cur = conn.cursor()
        cur.execute("SELECT * FROM reports")
        print(cur.fetchall())

        return

    # Read regression algorithms from file
    try:
        with open('regression_devices.pickle', 'rb') as f:
            dev_reg = pickle.load(f)
    except:
        dev_reg = linear_model.SGDRegressor(loss="huber", epsilon=0.075)
    try:
        with open('regression_people.pickle', 'rb') as f:
            peo_reg = pickle.load(f)
    except:
        peo_reg = linear_model.SGDRegressor(loss="huber", epsilon=0.075)

    # Iterate over reports and update regression algorithms
    for rpirs in reports:
        for report in rpirs:
            print ("adding report :")
            print ("\t" + str(report))
            people = report[3]
            devices = report[4]

            if (people != None):
                print ("updated people regression")
                peo_reg.partial_fit(np.array(people), np.array(value).reshape(-1,1))

            if (devices != None):
                print ("updated device regression")
                dev_reg.partial_fit(np.array(devices), np.array(value).reshape(-1,1))


    # Save modified regression algorithm to file
    with open('regression_devices.pickle', 'wb') as f:
        pickle.dump(dev_reg, f, protocol=pickle.HIGHEST_PROTOCOL)
    with open('regression_people.pickle', 'wb') as f:
        pickle.dump(peo_reg, f, protocol=pickle.HIGHEST_PROTOCOL)

    return


def makePredictions():

    # Get list of all rooms
    conn = aquireSQLConnection("reports")
    cur = conn.cursor()

    # Get all rooms
    cur.execute("SELECT id FROM rooms;")
    ans = cur.fetchall()

    print ("making predictions on rooms: ")
    print (str(ans))

    # Make predictions for each
    for room in ans:
        makeRoomPrediction(room[0])


def makeRoomPrediction(room):

    print("predicting room " + str(room))

    # Get all rpis in room
    conn = aquireSQLConnection("reports")
    cur = conn.cursor()
    cur.execute("SELECT id FROM rpis AS r WHERE r.roomID = {};".format(room))
    ans = cur.fetchall()

    time_l = time.time() - 300
    # Get all reports from rpis
    reports = []
    if (ans == ()):
        print ("no rpis")
        return

    for rpi in ans[0]:
        cur = conn.cursor()
        print ("SELECT * FROM reports AS r WHERE r.rpiID = {} AND r.time > {};".format(rpi, int(time_l)))
        cur.execute("SELECT * FROM reports AS r WHERE r.rpiID = {} AND r.time > {};".format(rpi, int(time_l)))
        reports.append(cur.fetchall())


    print (reports)
    if (reports == []):
        print ("no reports")
        return

    # Get regression algorithms
    try:
        with open('regression_devices.pickle', 'rb') as f:
            dev_reg = pickle.load(f)
    except:
        print ("No device regression algorithm found!")
        return
    try:
        with open('regression_people.pickle', 'rb') as f:
            peo_reg = pickle.load(f)
    except:
        print ("No people regression algorithm found!")
        return

    # Take average of people and devices
    averages = []
    for rpi in reports:
        total_people = None
        people_count = 0
        total_devices = None
        device_count = 0
        for report in rpi:
            print (report)
            if (report[3] != None):
                people_count += 1
                if total_people == None:
                    total_people = report[3]
                else:
                    total_people += report[3]
            if (report[4] != None):
                device_count += 1
                if total_devices== None:
                    total_devices = report[4]
                else:
                    total_devices += report[4]
        if (total_people != None):
            total_people = total_people/people_count
        if (total_devices != None):
            total_devices = total_devices/people_count
        averages.append([total_people, total_devices])

    # Perform prediction for each average
    ppredictions = []
    dpredictions = []
    for average in averages:

        print ("-----")
        print (averages)
        # Perform linear regression for people
        prediction = peo_reg.predict(average[0])
        ppredictions.append(prediction)

        # Perform linear regression for devices
        prediction = dev_reg.predict(average[1])
        dpredictions.append(prediction)

    # Take average of types of predictions
    print(ppredictions)
    print(dpredictions)

    pprediction = np.average(ppredictions)
    dprediction = np.average(dpredictions)

    # Take average of final predictions
    prediction = np.average([pprediction, dprediction])

    # Write to database
    conn = aquireSQLConnection("reports")
    cur = conn.cursor()

    cur.executemany("INSERT INTO estimates (roomID,time,estimate) VALUES (%s, %s, %s)", [(room,time.time(),prediction,)])
    ans = cur.fetchall()
    conn.commit()

    return



#-- Auxilary code for testing --#

def getDatabaseName():
    return database


def setDatabaseName(name):
    global database
    database = name


if __name__ == "__main__":
    app.run(host='0.0.0.0', threaded=True)
