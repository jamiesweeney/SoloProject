// Dom Elements
// Tables
var adminpanel = document.getElementById("admin-panel");
var buildingTable = document.getElementById("admin-buildings").childNodes[3];
var floorTable = document.getElementById("admin-floors").childNodes[3];
var roomTable = document.getElementById("admin-rooms").childNodes[3];
var rpiTable = document.getElementById("admin-rpis").childNodes[3];
var userTable = document.getElementById("admin-users").childNodes[3];

// Table titles
var floorTitle = document.getElementById("admin-floors-title")
var roomTitle = document.getElementById("admin-rooms-title")
var rpiTitle = document.getElementById("admin-rpis-title")

// Input elements for adding new buildings/floors/rooms/rpis
var newBuildingName =  document.getElementById("new-building-name");
var newBuildingDesc =  document.getElementById("new-building-desc");

var newFloorName =  document.getElementById("new-floor-name");
var newFloorDesc =  document.getElementById("new-floor-desc");

var newRoomName =  document.getElementById("new-room-name");
var newRoomDesc =  document.getElementById("new-room-desc");

var newRpiName =  document.getElementById("new-rpi-name");
var newRpiDesc =  document.getElementById("new-rpi-desc");

var newUserName = document.getElementById("new-user-name");
var newUserPass1 = document.getElementById("new-user-pass1");
var newUserPass2 = document.getElementById("new-user-pass2");




// Api Endpoints
// Get urls
var base_url = window.location.hostname
var buildings_url =  "/api/v1/buildings/get-all"
var building_url = "/api/v1/buildings/admin-get/"
var users_url = "/api/v1/users/admin-get-all"
var rpis_url = "/api/v1/rpis/admin-get-all"

// Post urls
var add_buildings_url = "/api/v1/buildings/admin-add"
var delete_buildings_url = "/api/v1/buildings/admin-delete"

var add_floors_url = "/api/v1/floors/admin-add"
var delete_floors_url = "/api/v1/floors/admin-delete"

var add_rooms_url = "/api/v1/rooms/admin-add"
var delete_rooms_url = "/api/v1/rooms/admin-delete"

var add_rpis_url = "/api/v1/rpis/admin-add"
var delete_rpis_url = "/api/v1/rpis/admin-delete"

var add_users_url = "/api/v1/users/admin-add"
var delete_users_url = "/api/v1/users/admin-delete"

// Triggers the intial database gets
getBuildings()
getUsers()

// Variables used to store current display data
buildings_dict = {}
selected_building = null
selected_floor = null
selected_room = null

// Functions for adding new elements to the DOM
// Puts the building data in the table
function addBuilding(resp){


  building = JSON.parse(resp)
  buildings_dict[building["id"]] = building

  // New building div
  var new_building = document.createElement("tr");

  // Fill ID
  var b_id = document.createElement("td")
  var t_node = document.createTextNode(building["id"]);
  b_id.appendChild(t_node)
  new_building.appendChild(b_id)

  // Fill name
  var b_name = document.createElement("td")
  var t_node = document.createTextNode(building["name"]);
  b_name.appendChild(t_node)
  new_building.appendChild(b_name)

  // Fill description
  var b_description = document.createElement("td")
  var t_node = document.createTextNode(building["description"]);
  b_description.appendChild(t_node)
  new_building.appendChild(b_description)

  // Fill #floors
  var b_floors = document.createElement("td")
  var t_node = document.createTextNode(building["floors"].length);
  b_floors.appendChild(t_node)
  new_building.appendChild(b_floors)

  // Get room count and rpi count by iterating through building data
  room_count = 0
  rpi_count = 0

  for (floor in building["floors"]){
    for (room in building["floors"][floor]["rooms"]){
      room_count += 1
      rpi_count += building["floors"][floor]["rooms"][room]["rpis"].length
    }
  }

  // Fill #rooms
  var b_rooms = document.createElement("td")
  var t_node = document.createTextNode(room_count.toString());
  b_rooms.appendChild(t_node)
  new_building.appendChild(b_rooms)

  // Fill #rpis
  var b_rpis = document.createElement("td")
  var t_node = document.createTextNode(rpi_count.toString());
  b_rpis.appendChild(t_node)
  new_building.appendChild(b_rpis)

  // Add tools
  var b_tools = document.createElement("td")

  // Delete tool
  var b_node = document.createElement("BUTTON")
  b_node.className = "admin-button-delete"
  var t_node = document.createElement("i")
  t_node.className="fa fa-trash"
  b_node.value = building["id"]
  b_node.onclick=function(){deleteBuilding(this.value)}
  b_node.appendChild(t_node)
  b_tools.appendChild(b_node)

  // Expand tool
  var b_node = document.createElement("BUTTON")
  b_node.className = "admin-button-expand"
  var t_node = document.createElement("i");
  t_node.className="fa fa-bars"
  b_node.value = building["id"]
  b_node.onclick=function(){expandBuilding(this.value)}
  b_node.appendChild(t_node)
  b_tools.appendChild(b_node)


  new_building.appendChild(b_tools)
  // Set class and id
  new_building.id = "admin-building"+building["id"]
  new_building.className = "admin-building"

  // Add to table
  buildingTable.appendChild(new_building)
}

// Puts the floor data in the table
function addFloor(resp){

  floor = resp

  // New floor div
  var new_floor = document.createElement("tr");

  // Fill building ID
  var b_id = document.createElement("td")
  var t_node = document.createTextNode(floor["building_id"]);
  b_id.appendChild(t_node)
  new_floor.appendChild(b_id)

  // Fill ID
  var f_id = document.createElement("td")
  var t_node = document.createTextNode(floor["floor_id"]);
  f_id.appendChild(t_node)
  new_floor.appendChild(f_id)

  // Fill name
  var f_name = document.createElement("td")
  var t_node = document.createTextNode(floor["floor_name"]);
  f_name.appendChild(t_node)
  new_floor.appendChild(f_name)

  // Fill description
  var f_description = document.createElement("td")
  var t_node = document.createTextNode(floor["floor_desc"]);
  f_description.appendChild(t_node)
  new_floor.appendChild(f_description)

  // Get room count and rpi count by iterating through building data
  room_count = 0
  rpi_count = 0

  for (room in floor["rooms"]){
      room_count += 1
      rpi_count += floor["rooms"][room]["rpis"].length
  }

  // Fill #rooms
  var f_rooms = document.createElement("td")
  var t_node = document.createTextNode(room_count.toString());
  f_rooms.appendChild(t_node)
  new_floor.appendChild(f_rooms)

  // Fill #rpis
  var f_rpis = document.createElement("td")
  var t_node = document.createTextNode(rpi_count.toString());
  f_rpis.appendChild(t_node)
  new_floor.appendChild(f_rpis)

  // Add tools
  var f_tools = document.createElement("td")

  // Delete tool
  var f_node = document.createElement("BUTTON")
  f_node.className = "admin-button-delete"
  var t_node = document.createElement("i")
  t_node.className="fa fa-trash"
  f_node.value = floor["floor_id"]
  f_node.onclick=function(){deleteFloor(this.value)}
  f_node.appendChild(t_node)
  f_tools.appendChild(f_node)

  // Expand tool
  var f_node = document.createElement("BUTTON")
  f_node.className = "admin-button-expand"
  var t_node = document.createElement("i");
  t_node.className="fa fa-bars"
  f_node.value = floor["floor_id"]
  f_node.onclick=function(){expandFloor(this.value)}
  f_node.appendChild(t_node)
  f_tools.appendChild(f_node)

  new_floor.appendChild(f_tools)

  // Set class and id
  new_floor.id = "admin-floor"+floor["floor_id"]
  new_floor.className = "admin-floor"

  // Add to table
  floorTable.appendChild(new_floor)

}

// Puts the room data in the table
function addRoom(resp){

  room = resp

  // New floor div
  var new_room = document.createElement("tr");

  // Fill building ID
  var b_id = document.createElement("td")
  var t_node = document.createTextNode(room["building_id"]);
  b_id.appendChild(t_node)
  new_room.appendChild(b_id)

  // Fill floor ID
  var f_id = document.createElement("td")
  var t_node = document.createTextNode(room["floor_id"]);
  f_id.appendChild(t_node)
  new_room.appendChild(f_id)

  // Fill ID
  var r_id = document.createElement("td")
  var t_node = document.createTextNode(room["room_id"]);
  r_id.appendChild(t_node)
  new_room.appendChild(r_id)

  // Fill name
  var r_name = document.createElement("td")
  var t_node = document.createTextNode(room["room_name"]);
  r_name.appendChild(t_node)
  new_room.appendChild(r_name)

  // Fill description
  var r_description = document.createElement("td")
  var t_node = document.createTextNode(room["room_desc"]);
  r_description.appendChild(t_node)
  new_room.appendChild(r_description)

  // Fill #rpis
  var r_rpis = document.createElement("td")
  var t_node = document.createTextNode(room["rpis"].length);
  r_rpis.appendChild(t_node)
  new_room.appendChild(r_rpis)

  // Add tools
  var r_tools = document.createElement("td")

  // Delete tool
  var r_node = document.createElement("BUTTON")
  r_node.className = "admin-button-delete"
  var t_node = document.createElement("i")
  t_node.className="fa fa-trash"
  r_node.value = room["room_id"]
  r_node.onclick=function(){deleteRoom(this.value)}
  r_node.appendChild(t_node)
  r_tools.appendChild(r_node)

  // Expand tool
  var r_node = document.createElement("BUTTON")
  r_node.className = "admin-button-expand"
  var t_node = document.createElement("i");
  t_node.className="fa fa-bars"
  r_node.value = room["room_id"]
  r_node.onclick=function(){expandRoom(this.value)}
  r_node.appendChild(t_node)
  r_tools.appendChild(r_node)

  new_room.appendChild(r_tools)

  // Set class and id
  new_room.id = "admin-room"+room["room_id"]
  new_room.className = "admin-room"

  // Add to table
  roomTable.appendChild(new_room)
}

// Puts the rpi data in the table
function addRpi(resp){

  rpi = resp

  // New rpi div
  var new_rpi = document.createElement("tr");

  // Fill building ID
  var b_id = document.createElement("td")
  var t_node = document.createTextNode(rpi["building_id"]);
  b_id.appendChild(t_node)
  new_rpi.appendChild(b_id)

  // Fill floor ID
  var f_id = document.createElement("td")
  var t_node = document.createTextNode(rpi["floor_id"]);
  f_id.appendChild(t_node)
  new_rpi.appendChild(f_id)

  // Fill room ID
  var r_id = document.createElement("td")
  var t_node = document.createTextNode(rpi["room_id"]);
  r_id.appendChild(t_node)
  new_rpi.appendChild(r_id)

  // Fill ID
  var r_id = document.createElement("td")
  var t_node = document.createTextNode(rpi["rpi_id"]);
  r_id.appendChild(t_node)
  new_rpi.appendChild(r_id)

  // Fill name
  var r_name = document.createElement("td")
  var t_node = document.createTextNode(rpi["rpi_name"]);
  r_name.appendChild(t_node)
  new_rpi.appendChild(r_name)

  // Fill description
  var r_description = document.createElement("td")
  var t_node = document.createTextNode(rpi["rpi_desc"]);
  r_description.appendChild(t_node)
  new_rpi.appendChild(r_description)

  // Fill last report
  var r_rep = document.createElement("td")
  var t_node = document.createTextNode("never");
  r_rep.appendChild(t_node)
  new_rpi.appendChild(r_rep)

  // Add tools
  var r_tools = document.createElement("td")

  // Delete tool
  var r_node = document.createElement("BUTTON")
  r_node.className = "admin-button-delete"
  var t_node = document.createElement("i")
  t_node.className="fa fa-trash"
  r_node.value = rpi["rpi_id"]
  r_node.onclick=function(){deleteRpi(this.value)}
  r_node.appendChild(t_node)
  r_tools.appendChild(r_node)

  // Download auth tool
  var data = "text/json;charset=utf-8," + encodeURIComponent(JSON.stringify({"id":rpi["rpi_id"], "auth_key": rpi["auth_key"]}));
  var r_node = document.createElement("BUTTON")
  r_node.className = "admin-button-download"
  var t_node = document.createElement("i")
  t_node.className="fa fa-download"
  var l_node = document.createElement("a")
  l_node.href = "data:"+ data
  l_node.download = rpi["rpi_name"] + ".json"
  r_node.value = rpi["rpi_id"]
  //r_node.onclick=function(){downloadRpiAuth(this.value)}
  l_node.appendChild(t_node)
  r_node.appendChild(l_node)
  r_tools.appendChild(r_node)
  new_rpi.appendChild(r_tools)

  // Set class and id
  new_rpi.id = "admin-rpi"+rpi["rpi_id"]
  new_rpi.className = "admin-rpi"

  // Add to table
  rpiTable.appendChild(new_rpi)
}

// Puts the user data in the table
function addUser(resp){
  user = resp

  // New user div
  var new_user = document.createElement("tr");

  // Fill ID
  var u_id = document.createElement("td")
  var t_node = document.createTextNode(user[0]);
  u_id.appendChild(t_node)
  new_user.appendChild(u_id)

  // Fill name
  var u_name = document.createElement("td")
  var t_node = document.createTextNode(user[1]);
  u_name.appendChild(t_node)
  new_user.appendChild(u_name)


  // Delete tool
  var u_tools = document.createElement("td")
  var u_node = document.createElement("BUTTON")
  u_node.className = "admin-button-delete"
  var t_node = document.createElement("i")
  t_node.className="fa fa-trash"
  u_node.value = user[0]
  u_node.onclick=function(){deleteUser(this.value)}
  u_node.appendChild(t_node)
  u_tools.appendChild(u_node)
  new_user.appendChild(u_tools)

  // Set class and id
  new_user.id = "admin-user"+user[0]
  new_user.className = "admin-user"

  // Add to table
  userTable.appendChild(new_user)
}


// Functions for handling get responses
// Handles a buildings response
function handleBuildings(resp){

  buildings_dict = {}

  // Decode JSON
  data = JSON.parse(resp)
  buildings = data["buildings"]

  // Add each building
  for (building in buildings){
    getBuildingData(buildings[building]["building_id"])
  }
}

// Handles a users response
function handleUsers(resp){

  // Decode JSON
  data = JSON.parse(resp)
  users = data["users"]

  // Add each building
  for (user in users){
    addUser(users[user])
  }
}


// Functions for making get requests
// Gets all data for one building
function getBuildingData(building_id){

  // Get building data, on sucess call handleBuildings
  url = building_url +  building_id.toString()
  var xmlHttp = new XMLHttpRequest();
  xmlHttp.onreadystatechange = function() {
      if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
          addBuilding(xmlHttp.responseText);
  }
  xmlHttp.open("GET", url, true); // true for asynchronous
  xmlHttp.send(null);

}

// Gets all buildings from server
function getBuildings(){

  // Reset the building table
  buildingTable.textContent = '';
  floorTable.textContent = '';
  roomTable.textContent = '';
  rpiTable.textContent = '';

  // Get all buildings, on sucess call getBuildingData
  url = buildings_url
  var xmlHttp = new XMLHttpRequest();
  xmlHttp.onreadystatechange = function() {
      if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
          handleBuildings(xmlHttp.responseText);
  }
  xmlHttp.open("GET", url, true); // true for asynchronous
  xmlHttp.send(null);
}

// Gets all users
function getUsers(){

  userTable.textContent = '';
  newUserName.textContent = '';
  newUserPass1.textContent = '';
  newUserPass2.textContent = '';

  // Get all users, call handleUsers on sucess
  url = users_url
  var xmlHttp = new XMLHttpRequest();
  xmlHttp.onreadystatechange = function() {
      if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
          handleUsers(xmlHttp.responseText);
  }
  xmlHttp.open("GET", url, true); // true for asynchronous
  xmlHttp.send(null);
}


// Functions for adding new objects to the database
// Send an add building request
function addNewBuilding(){

  name = newBuildingName.value
  desc = newBuildingDesc.value

  // Make request, on sucess get all buildings again
  url = add_buildings_url
  $.ajax({
    type: 'POST',
    url: url,
    data: JSON.stringify({"name":name, "description":desc}),
    success: function(result) {
       getBuildings()
    }
});
}

// Send an add floor request
function addNewFloor(){

  building_id = selected_building
  name = newFloorName.value
  desc = newFloorDesc.value

  // Make request, on sucess get all floors again
  url = add_floors_url
  $.ajax({
    type: 'POST',
    url: url,
    data: JSON.stringify({"building_id":building_id,"name":name, "description":desc}),
    success: function(result) {
      sel = selected_building
      getBuildings()

      expandBuilding(sel)
    }
  });
}

// Send an add room request
function addNewRoom(){

  floor_id = selected_floor
  name = newRoomName.value
  desc = newRoomDesc.value

  // Make request, on sucess get all buildings again
  url = add_rooms_url
  $.ajax({
    type: 'POST',
    url: url,
    data: JSON.stringify({"floor_id":floor_id,"name":name, "description":desc}),
    success: function(result) {
      sel = selected_building
      sel2 = selected_floor
      getBuildings()
      expandBuilding(sel)
      expandFloor(sel2)
    }
});
}

// Send an add rpi request
function addNewRpi(){

  room_id = selected_room
  name = newRpiName.value
  desc = newRpiDesc.value

  // Make request, on sucess get all buildings again
  url = add_rpis_url
  $.ajax({
    type: 'POST',
    url: url,
    data: JSON.stringify({"room_id":room_id,"name":name, "description":desc}),
    success: function(result) {
      sel = selected_building
      sel2 = selected_floor
      sel3 = selected_room
      getBuildings()
      expandBuilding(sel)
      expandFloor(sel2)
      expandRoom(sel3)
    }
});
}

// Send an add user request
function addNewUser(){

  user_name = newUserName.value
  pass1 = newUserPass1.value
  pass2 = newUserPass2.value

  // Make sure password is safe
  if (pass1 != pass2){
    console.log("Entered passwords do not match, try again!")
    return
  }else if (pass1.replace(" ", "") == ""){
    console.log("Password not secure, try again!")
  }

  // Make request, on sucess get all users again
  url = add_users_url
  $.ajax({
    type: 'POST',
    url: url,
    data: JSON.stringify({"username":user_name,"password":pass1}),
    success: function(result) {
      getUsers()
    }
});
}

// Functions for deleting objects from the database
// Send a delete buudling request
// Send a delete building request
function deleteBuilding(id){

  if (confirm("Are you sure you want to delete building " + id + " and all references?") == false){
    return
  }

  // Make request, on sucess get all buildings again
  url = delete_buildings_url
  $.ajax({
    type: 'POST',
    url: url,
    data: JSON.stringify({"id":id}),
    success: function(result) {
       getBuildings()
    }
});
}

// Send a delete floor request
function deleteFloor(id){

  if (confirm("Are you sure you want to delete floor " + id + " and all references?") == false){
    return
  }

  // Make request, on sucess get all buildings again
  url = delete_floors_url
  $.ajax({
    type: 'POST',
    url: url,
    data: JSON.stringify({"id":id}),
    success: function(result) {
      sel = selected_building
      getBuildings()
      expandBuilding(sel)
    }
});
}

// Send a delete room request
function deleteRoom(id){

  if (confirm("Are you sure you want to delete room " + id + " and all references?") == false){
    return
  }

  // Make request, on sucess get all buildings again
  url = delete_rooms_url
  $.ajax({
    type: 'POST',
    url: url,
    data: JSON.stringify({"id":id}),
    success: function(result) {
      sel = selected_building
      sel2 = selected_floor
      getBuildings()
      expandBuilding(sel)
      expandFloor(sel2)
    }
});
}

// Send a delete rpi request
function deleteRpi(id){

  if (confirm("Are you sure you want to delete rpi " + id + " and all references?") == false){
    return
  }

  // Make request, on sucess get all buildings again
  url = delete_rpis_url
  $.ajax({
    type: 'POST',
    url: url,
    data: JSON.stringify({"id":id}),
    success: function(result) {
      sel = selected_building
      sel2 = selected_floor
      sel3 = selected_room
      getBuildings()
      expandBuilding(sel)
      expandFloor(sel2)
      expandRoom(sel3)
    }
});
}

// Send a delete rpi request
function deleteUser(id){

  if (!confirm("Are you sure you want to delete user " + id + " and all references?")){
    return
  }

  // Make request, on sucess get all users again
  url = delete_users_url
  $.ajax({
    type: 'POST',
    url: url,
    data: JSON.stringify({"id":id}),
    success: function(result) {
      getUsers()
    }
});
}


// Functions for expanding object to new tables
// Expand a building
function expandBuilding(id){

  selected_building = id
  building_data = buildings_dict[id.toString()]

  floorTable.textContent = '';
  roomTable.textContent = '';
  rpiTable.textContent = '';
  floorTable.parentNode.style.visibility = "visible"
  floorTitle.style.visibility = "visible"
  floorTitle.innerText = building["name"]

  for (floor in building_data["floors"]){
    addFloor(building_data["floors"][floor])
  }


}

// Expand a floor
function expandFloor(id){

  selected_floor = id
  building_data = buildings_dict[selected_building.toString()]

  for (floor in building_data["floors"]){
    if (building_data["floors"][floor]["floor_id"] == id){
      floor_data = building_data["floors"][floor]
      break;
    }
  }

  roomTable.textContent = '';
  rpiTable.textContent = '';
  roomTable.parentNode.style.visibility = "visible"
  roomTitle.style.visibility = "visible"
  roomTitle.innerText = floor_data["floor_name"]

  for (room in floor_data["rooms"]){
    addRoom(floor_data["rooms"][room])
  }
}

// Expand a room
function expandRoom(id){

  selected_room = id
  building_data = buildings_dict[selected_building.toString()]
  for (floor in building_data["floors"]){
    if (building_data["floors"][floor]["floor_id"] == selected_floor){
      floor_data = building_data["floors"][floor]
      for (room in floor_data["rooms"]){
        if (floor_data["rooms"][room]["room_id"] == id){
          room_data = floor_data["rooms"][room]
          break
        }
      }
      break;
    }
  }


  rpiTable.textContent = '';
  rpiTable.parentNode.style.visibility = "visible"
  rpiTitle.style.visibility = "visible"
  rpiTitle.innerText = room_data["room_name"]

  for (rpi in room_data["rpis"]){
    addRpi(room_data["rpis"][rpi])
  }
}


// Downloads the rpi auth data
function downloadRpiAuth(id){

  building_data = buildings_dict[selected_building.toString()]
  for (floor in building_data["floors"]){
    if (building_data["floors"][floor]["floor_id"] == selected_floor){
      floor_data = building_data["floors"][floor]
      for (room in floor_data["rooms"]){
        if (floor_data["rooms"][room]["room_id"] == selected_room){
          room_data = floor_data["rooms"][room]
          for (rpi in room_data["rpis"]){
            if (room_data["rpis"][rpi]["rpi_id"] == id){
              rpi_data = room_data["rpis"][rpi]
              break
            }
          }
          break
        }
      }
      break;
    }
  }


}
