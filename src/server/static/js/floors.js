
// Dom Elements
var floorContainer = document.getElementById("floors");

// Api Endpoints
var base_url ="http://127.0.0.1:5000"
var building_url = base_url + "/api/v1/buildings/get/"
var floor_url = base_url + "/api/v1/floors/get/"
var est_url = base_url + "/api/v1/rooms/get_estimate/"

var floors_page = base_url + "/webapp/floor/"

var curr_url = window.location.href.split("/")
var building_id = curr_url.slice(-1)[0]



getFloors()


function addReport(report, floor_id){

  // Get floor div
  console.log("floor"+floor_id)
  var floor_div = document.getElementById("floor"+floor_id)

  if (report["estimate"] == "NULL"){
    floor_div.totalOccupants = floor_div.totalOccupants
  }else{
    floor_div.totalOccupants = parseInt(floor_div.totalOccupants) + parseInt(report["estimate"])
  }

  var n = document.createElement("p")
  var t_node = document.createTextNode(report["estimate"]);

  n.appendChild(t_node)
  floor_div.appendChild(n)


}

function handleEstimate(resp, floor_id){

  // Decode JSON
  data = JSON.parse(resp)
  report = data["report"]

  addReport(report, floor_id)
}

function getEstimate(room_id, floor_id){


  url = est_url + room_id
  console.log(url)
  var xmlHttp = new XMLHttpRequest();
  xmlHttp.onreadystatechange = function() {
      if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
          handleEstimate(xmlHttp.responseText, floor_id);
  }
  xmlHttp.open("GET", url, true); // true for asynchronous
  xmlHttp.send(null);
}


function handleRooms(resp, floor_id){

  // Decode JSON
  data = JSON.parse(resp)
  rooms = data["rooms"]

  // Add each room
  for (room in rooms){
    getEstimate(rooms[room]["room_id"], floor_id)
  }
}


function getRooms(floor_id){

  url = floor_url + floor_id
  var xmlHttp = new XMLHttpRequest();
  xmlHttp.onreadystatechange = function() {
      if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
          handleRooms(xmlHttp.responseText, floor_id);
  }
  xmlHttp.open("GET", url, true); // true for asynchronous
  xmlHttp.send(null);
}


function addFloor(floor){

  // New building div
  var new_floor = document.createElement("div");
  new_floor.id = "floor"+floor["floor_id"]
  new_floor.className = "floor"
  new_floor.totalOccupants = "NULL"

  // Name para
  var name = document.createElement("p")
  var t_node = document.createTextNode(floor["floor_name"]);
  name.appendChild(t_node)
  new_floor.appendChild(name)

  // Add link
  new_floor.addEventListener('click', function(){
      window.location.href = floors_page + floor["floor_id"]
  });

  // Add to box
  floorContainer.appendChild(new_floor)

  // Get room data for floor
  getRooms(floor["floor_id"])
}

function handleFloors(resp){

  // Decode JSON
  data = JSON.parse(resp)
  floors = data["floors"]

  // Add each building
  for (floor in floors){
    addFloor(floors[floor])
  }
}

function getFloors(){
  url = building_url + building_id
  var xmlHttp = new XMLHttpRequest();
  xmlHttp.onreadystatechange = function() {
      if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
          handleFloors(xmlHttp.responseText);
  }
  xmlHttp.open("GET", url, true); // true for asynchronous
  xmlHttp.send(null);
}
