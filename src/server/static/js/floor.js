
// Dom Elements
var roomContainer = document.getElementById("rooms");

// Api Endpoints
var base_url = window.location.hostname
var building_url = "/api/v1/buildings/get/"
var floor_url = "/api/v1/floors/get/"
var est_url = "/api/v1/rooms/get-estimate/"

var room_page = "/webapp/room/"

var curr_url = window.location.href.split("/")
var floor_id = curr_url.slice(-1)[0]

var room_count = 0

// Get room data for floor
getRooms(floor_id)


function addEstimate(estimate, room_id){

  // Get room div
  console.log("room"+room_id)
  var room_div = document.getElementById("room"+room_id)
  console.log(estimate["estimate"])

  if (estimate["estimate"] == null){
    room_div.totalOccupants = "???"
  }else if (isNaN(parseInt(estimate["estimate"]["estimate"]))){
    console.log((isNaN(parseInt(estimate["estimate"]["estimate"]))))
    room_div.totalOccupants = "???"
  }else{
    room_div.totalOccupants = parseInt(estimate["estimate"]["estimate"])
  }

  oc = room_div.totalOccupants
  console.log(oc)

  if (oc == 0){
    room_div.style.background = "white"
  }else if(oc <= 25) {
    room_div.style.background = "seagreen"
  }else if(oc <= 50) {
    room_div.style.background = "orange"
  }else if(oc <= 75) {
    room_div.style.background = "orangered"
  }else if(oc > 75) {
    room_div.style.background = "red"
  }else {
    room_div.style.background = "grey"
  }

  roomNum = room_div.childNodes[1]
  roomNum.childNodes[0].textContent = "Total: " + room_div.totalOccupants
}

function handleEstimate(resp, room_id){

  // Decode JSON
  data = JSON.parse(resp)
  estimate = data

  addEstimate(estimate, room_id)
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

  room_count = room_count + 1

  // New building div
  var new_room = document.createElement("div");
  new_room.id = "room"+room["room_id"]
  new_room.className = "room"
  new_room.totalOccupants = "NULL"

  // room name
  var name_div = document.createElement("div")
  name_div.className = "roomName"
  var name = document.createElement("h1")
  var t_node = document.createTextNode(room["room_name"]);
  name.appendChild(t_node)
  name_div.appendChild(name)
  new_room.appendChild(name_div)

  // Total number
  var num_div = document.createElement("div")
  num_div.className = "roomNum"
  var num = document.createElement("h1")
  var t_node = document.createTextNode("Total: ???");
  num.appendChild(t_node)
  num_div.appendChild(num)
  new_room.appendChild(num_div)

  // Add link
  new_room.addEventListener('click', function(){
      window.location.href = room_page + room["room_id"]
  });

  // Add to box
  roomContainer.appendChild(new_room)

  // If an odd number of rooms, add space in between
  if (room_count % 2 == 1){
    var room_space = document.createElement("div")
    room_space.className = "roomSpace"

    // Add to box
    roomContainer.appendChild(room_space)
  }

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
