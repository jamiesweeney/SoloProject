
// Dom Elements
var roomContainer = document.getElementById("rooms");

// Api Endpoints
var base_url = "http://" + window.location.hostname +":5000"

var building_url = base_url + "/api/v1/buildings/get/"
var floor_url = base_url + "/api/v1/floors/get/"
var est_url = base_url + "/api/v1/rooms/get_estimate/"

var room_page = base_url + "/webapp/room/"

var curr_url = window.location.href.split("/")
var floor_id = curr_url.slice(-1)[0]


// Get room data for floor
getRooms(floor_id)


function addReport(report, room_id){

  // Get floor div
  console.log("room"+room_id)
  var room_div = document.getElementById("room"+room_id)

  if (report["estimate"] == "NULL"){
    room_div.totalOccupants = room_div.totalOccupants
  }else{
    room_div.totalOccupants = parseInt(report["estimate"])
  }

  var n = document.createElement("p")
  var t_node = document.createTextNode(report["estimate"]);

  n.appendChild(t_node)
  room_div.appendChild(n)
}

function handleEstimate(resp, room_id){

  // Decode JSON
  data = JSON.parse(resp)
  report = data["report"]

  addReport(report, room_id)
}

function getEstimate(room_id){


  url = est_url + room_id
  var xmlHttp = new XMLHttpRequest();
  xmlHttp.onreadystatechange = function() {
      if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
          handleEstimate(xmlHttp.responseText, room_id);
  }
  xmlHttp.open("GET", url, true); // true for asynchronous
  xmlHttp.send(null);
}


function addRoom(room){

  // New building div
  var new_room = document.createElement("div");
  new_room.id = "room"+room["room_id"]
  new_room.className = "room"
  new_room.totalOccupants = "NULL"

  // Name para
  var name = document.createElement("p")
  var t_node = document.createTextNode(room["room_name"]);
  name.appendChild(t_node)
  new_room.appendChild(name)

  // Add link
  new_room.addEventListener('click', function(){
      window.location.href = room_page + room["room_id"]
  });

  // Add to box
  roomContainer.appendChild(new_room)

  // Get room estimate
  getEstimate(room["room_id"])
}


function handleRooms(resp, floor_id){

  // Decode JSON
  data = JSON.parse(resp)
  rooms = data["rooms"]

  // Add each room
  for (room in rooms){
    addRoom(rooms[room])
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
