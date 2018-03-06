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


#-- Web pages --#
# Index page - redirects to home
@app.route("/")
def wp_index():
    return redirect("webapp/home", code=302)

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

# Admin page - all the admin tools
@app.route("/webapp/admin")
@login_required     # Important
def wp_admin():

    return render_template('/html/admin.html')

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
            return redirect(url_for("wp_login", warning="Details are invalid!"))

    # If not a POST request serve the login page
    else:
        return render_template("/html/login.html")

# Logout page - allows current user to log out, redirects to home
@app.route("/webapp/logout")
@login_required     # Important
def wp_logout():
    logout_user()
    return redirect("/webapp/home")


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
    cur.execute("SELECT floorID, id, name,s description FROM rooms AS r WHERE r.floorID = {};".format(floor_id))
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
#TODO - Fix this
def getRoom(room_id):

    # Get connection and cursor to DB
    conn = aquireSQLConnection("reports")
    cur = conn.cursor()

    # Get
    cur.execute("SELECT * FROM reports AS r WHERE r.roomID = {} ORDER BY r.time DESC LIMIT 20;".format(room_id))
    ans = cur.fetchall()

    reports = []
    for report in ans:
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
#TODO - Fix this
def getRoomEstimate(room_id):

    # Get connection and cursor to DB
    conn = aquireSQLConnection("reports")
    cur = conn.cursor()

    cur.execute("SELECT * FROM reports AS r WHERE r.roomID = {} ORDER BY r.time DESC LIMIT 1;".format(room_id))
    ans = cur.fetchone()

    report = ans
    info = {"room_id": report[0], "time": report[2], "estimate" : report[5]}

    data = {"report": info}

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

    # Get user data from JSON
    content = json.loads(str(request.get_data().decode("utf-8")))

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

    # Connect to SQL database using login and ssl-certs
    conn = MySQLdb.connect(host=host,
                         user=user,
                         passwd=password,
                         db=db_name,
                         ssl=ssl)
    return conn


#-- Linear regression --#
# Takes RPi output data and returns a guess of room occupancy based on linear reg alg.
def magic_algorithm(room_id, time_n, devices, people):
    return (random.randint(0,100))


if __name__ == "__main__":
    app.run(host='0.0.0.0', threaded=True)
