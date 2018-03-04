import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flask import Flask
from subprocess import call
from subprocess import check_output
import random
from flask import request,  render_template, json, redirect, Response, url_for
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, confirm_login
from urllib.parse import urlparse, urljoin
import MySQLdb
from passlib.hash import sha256_crypt
import json

app = Flask(__name__)

# config
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

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "wp_login"

print (dir(login_manager))

#-- Web pages --#
@app.route("/")
def wp_index():
    return redirect("webapp/home", code=302)

@app.route("/webapp/home")
def wp_home():
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

@app.route("/webapp/admin")
def wp_admin():
    return render_template('/html/admin.html')

@app.route("/webapp/login", methods=["GET", "POST"])
def wp_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        print ("# Got username and password:   " + str(username) + "   " + str(password))

        if (doLogin(username, password)):
            print ("Authentication sucess")

            # Get connection and cursor to DB
            conn = aquireSQLConnection("users")
            cur = conn.cursor()

            # Get user data from database
            cur.execute("SELECT userID FROM users AS u WHERE u.username = \'{}\';".format(username))
            ans = cur.fetchone()

            usr = User(username,ans[0] )
            print (usr.is_active())
            print (usr.is_anonymous())
            print (usr.is_authenticated())
            print (usr.get_id())

            login_user(usr)
            print ("--Logged in user " + str(username))
            next = request.args.get('next')
            print ("--With next=" + str(next))
            if is_safe_url(next):
                return redirect(next)

            return redirect(url_for("wp_home"))

        else:
            print ("Authentication failed")
            return redirect("/webapp/login")

    else:
        return render_template("/html/login.html")

@app.route("/webapp/logout")
@login_required
def wp_logout():
    logout_user()
    return redirect("/webapp/home")


#-- Public get requests --#
# Returns all the buildings
# Returns the list of all buildings
@app.route("/api/v1/buildings/get-all")
def getAllBuildings():

    # Get connection and cursor to DB
    conn = aquireSQLConnection("reports")
    cur = conn.cursor()

    cur.execute("SELECT id,name,description FROM buildings;")
    ans = cur.fetchall()

    buildings = []
    for building in ans:
        info = {"building_id": building[0], "building_name": building[1], "building_desc": building[2]}
        buildings.append(info)
    data = {}
    data = {"buildings": buildings}

    print (data)

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

    cur.execute("SELECT buildingID,id,name,description FROM floors AS f WHERE f.buildingID = {};".format(building_id))
    ans = cur.fetchall()

    floors = []
    for floor in ans:
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

    # Get connection and cursor to DB
    conn = aquireSQLConnection("reports")
    cur = conn.cursor()

    cur.execute("SELECT floorID, id, name,s description FROM rooms AS r WHERE r.floorID = {};".format(floor_id))
    ans = cur.fetchall()

    rooms = []
    for room in ans:
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

    # Get connection and cursor to DB
    conn = aquireSQLConnection("reports")
    cur = conn.cursor()

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
#@login_required
def adminGetBuilding(building_id):

    # Get connection and cursor to DB
    conn = aquireSQLConnection("reports")
    cur = conn.cursor()

    # Get building data
    cur.execute("SELECT name, description FROM buildings AS b WHERE b.id = {};".format(building_id))
    ans = cur.fetchall()

    building = {"id":building_id, "name": ans[0][0], "description": ans[0][1], "floors":[]}

    # Get each floor
    cur.execute("SELECT name, id, description FROM floors AS f WHERE f.buildingID = {};".format(building_id))
    ans = cur.fetchall()

    for floor in ans:
        floor_id = floor[1]
        info = {"building_id": building_id, "floor_id": floor[1], "floor_name": floor[0], "floor_desc" : floor[2], "rooms":[]}

        # Get each room
        cur.execute("SELECT name, id, description FROM rooms AS r WHERE r.floorID = {};".format(floor_id))
        rooms = cur.fetchall()

        for room in rooms:
            room_id = room[1]
            room_info = {"building_id": building_id, "floor_id": floor_id, "room_id": room[1], "room_name": room[0], "room_desc" : room[2], "rpis":[]}

            # Get each rpi
            cur.execute("SELECT name, id, description, auth_key FROM rpis AS r WHERE r.roomID = {};".format(room_id))
            rpis = cur.fetchall()

            for rpi in rpis:
                rpi_info = {"building_id": building_id, "floor_id": floor_id, "room_id": room_id, "rpi_id": rpi[1], "rpi_name": rpi[0], "rpi_desc": rpi[2], "auth_key": rpi[3]}

                room_info["rpis"].append(rpi_info)
            info["rooms"].append(room_info)
        building["floors"].append(info)

    # Return the data
    return app.response_class(
        response=json.dumps(building),
        status=200,
        mimetype='application/json'
    )

@app.route("/api/v1/buildings/admin-add", methods=['POST'])
#@login_required
def adminAddBuilding():

    content = json.loads(str(request.get_data().decode("utf-8")))

    # Get connection and cursor to DB
    conn = aquireSQLConnection("reports")
    cur = conn.cursor()

    # Add building to database
    cur.executemany("INSERT INTO buildings (name, description) VALUES (%s, %s)", [(content["name"], content["description"])])
    ans = cur.fetchall()

    conn.commit()
    return "OK"

@app.route("/api/v1/buildings/admin-delete", methods=['POST'])
#@login_required
def adminDelBuilding():

    content = json.loads(str(request.get_data().decode("utf-8")))

    # Get connection and cursor to DB
    conn = aquireSQLConnection("reports")
    cur = conn.cursor()

    # Add building to database
    cur.execute("DELETE FROM buildings WHERE id = {};".format(content["id"]))
    ans = cur.fetchall()

    conn.commit()
    return "OK"



# Returns admin data for users
@app.route("/api/v1/users/admin-get-all")
#@login_required
def adminGetUsers():
    # Get connection and cursor to DB
    conn = aquireSQLConnection("users")
    cur = conn.cursor()

    # Get building data
    cur.execute("SELECT userID, username FROM users;".format())
    ans = cur.fetchall()
    ans = {"users":ans}
    response = app.response_class(
        response=json.dumps(ans),
        status=200,
        mimetype='application/json'
    )
    return response

# Returns admin data for RPi auth
@app.route("/api/v1/rpis/admin-get-all")
#@login_required
def adminGetRPIs():
    return "Not implemented yet"


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


    # Get connection and cursor to DB
    conn = aquireSQLConnection("reports")
    cur = conn.cursor()

    cursor.executemany("INSERT INTO reports (roomID, time, devices, people, estimate) VALUES (%s, %s, %s, %s, %s)", [(room_id, time_n, devices, people, ans)])
    ans = cur.fetchall()

    conn.commit()
    return "OK"


#-- Authentication --#
# Authenticates the RPi requests for data changes
def magic_authentication(request):
    return True


# Authenticates users for admin access
def doLogin(username, password):

    if (username == None or password == None):
        return False

    # Get connection and cursor to DB
    conn = aquireSQLConnection("users")
    cur = conn.cursor()

    print (username)
    cur.execute("SELECT passhash  FROM users AS u WHERE u.username = \'{}\';".format(username))
    ans = cur.fetchone()
    if (ans != None):
        return sha256_crypt.verify(password, ans[0])
    else:
        return False


# User model
class User(UserMixin):
    def __init__(self, name, id, active=True):
        self.name = name
        self.id = id
        self.active = active

    def is_active(self):
        return True

    def is_anonymous(self):
        return True

    def is_authenticated(self):
        return True

    def get_id(self):
        return str(self.id).encode("utf-8").decode("utf-8")


# Loads a User object
@login_manager.user_loader
def load_user(username):

    # Get connection and cursor to DB
    conn = aquireSQLConnection("users")
    cur = conn.cursor()

    # Get user data from database
    cur.execute("SELECT userID, username FROM users AS u WHERE u.username = \'{}\';".format(username))
    ans = cur.fetchone()

    if (ans != None):
        user_id = ans[0]
        username = ans[1]

        # Create user object and return
        return User(username,user_id)




@login_manager.request_loader
def request_loader(request):

    username = request.form['username']
    password = request.form['password']

    if (doLogin(username, password)):
        # Get connection and cursor to DB
        conn = aquireSQLConnection("users")
        cur = conn.cursor()

        # Get user data from database
        cur.execute("SELECT userID, username FROM users AS u WHERE u.username = \'{}\';".format(username))
        ans = cur.fetchone()

        user = User(ans[1],ans[0])
        return user


# Checks if a redirect url is safe to redirect to
def is_safe_url(next):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, next))
    return test_url.scheme in ('https') and \
           ref_url.netloc == test_url.netloc and \
           next != None


#-- Database Management --#

# Gets an SQL connection to use for a DB --#
def aquireSQLConnection(db_name):

    # Connect to SQL database using login and ssl-certs
    conn = MySQLdb.connect(host=host,
                         user=user,
                         passwd=password,
                         db=db_name,
                         ssl=ssl)

    return conn


#-- Linear Regression --#
# Takes RPi output data and returns a guess of room occupancy based on linear reg alg.
def magic_algorithm(room_id, time_n, devices, people):
    return (random.randint(0,100))


if __name__ == "__main__":
    app.run(host='0.0.0.0', threaded=True)
