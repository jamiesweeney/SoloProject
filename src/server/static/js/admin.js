// Dom Elements
var adminpanel = document.getElementById("admin-panel");
var buildingTable = document.getElementById("admin-buildings").childNodes[3];
var userTable = document.getElementById("admin-users").childNodes[3];
var rpiTable = document.getElementById("admin-rpis").childNodes[3];


var newBuildingName =  document.getElementById("new-building-name");
var newBuildingDesc =  document.getElementById("new-building-desc");

// Api Endpoints
var base_url = window.location.hostname
var buildings_url =  "/api/v1/buildings/get-all"
var building_url = "/api/v1/buildings/admin-get/"
var users_url = "/api/v1/users/admin-get-all"
var rpis_url = "/api/v1/rpis/admin-get-all"

var add_buildings_url = "/api/v1/buildings/admin-add"
var delete_buildings_url = "/api/v1/buildings/admin-delete"


getBuildings()
getUsers()
getRpis()


// Puts the building data in the table
function addBuilding(resp){
  building = JSON.parse(resp)

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
  var b_node = document.createElement("BUTTON")
  var t_node = document.createTextNode("DELETE");
  b_node.value = building["id"]
  b_node.onclick=function(){deleteBuilding(this.value)}
  b_node.appendChild(t_node)
  b_tools.appendChild(b_node)
  new_building.appendChild(b_tools)

  // Set class and id
  new_building.id = "admin-building"+building["id"]
  new_building.className = "admin-building"

  // Add to table
  buildingTable.appendChild(new_building)
}

// Handles a building response
function handleBuildings(resp){

  // Decode JSON
  data = JSON.parse(resp)
  buildings = data["buildings"]

  // Add each building
  for (building in buildings){
    getBuildingData(buildings[building]["building_id"])
  }
}

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


  // Add tools
  var u_tools = document.createElement("td")
  new_user.appendChild(u_tools)

  // Set class and id
  new_user.id = "admin-user"+user[0]
  new_user.className = "admin-user"

  // Add to table
  userTable.appendChild(new_user)
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

// Gets all users
function getUsers(){

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



function addRpi(resp){
  console.log(resp)
}

function handleRpis(resp){
  // Decode JSON
  data = JSON.parse(resp)
  rpis = data["rpis"]

  // Add each building
  for (rpi in rpis){
    addRpi(rpis[rpi])
  }
}

function getRpis(){
  url = rpis_url
  var xmlHttp = new XMLHttpRequest();
  xmlHttp.onreadystatechange = function() {
      if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
          handleRpis(xmlHttp.responseText);
  }
  xmlHttp.open("GET", url, true); // true for asynchronous
  xmlHttp.send(null);
}



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

// Send a delete buudling request
function deleteBuilding(id){

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
