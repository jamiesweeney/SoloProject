
// Dom Elements
var floorContainer = document.getElementById("floors");

// Api Endpoints
var base_url = window.location.hostname
var building_url = "/api/v1/buildings/get/"
var floor_url = "/api/v1/floors/get/"
var est_url = "/api/v1/rooms/get_estimate/"

var floors_page = "/webapp/floor/"

var curr_url = window.location.href.split("/")
var building_id = curr_url.slice(-1)[0]



getFloors()


function addReport(estimate, floor_id){

  // Get floor div
  console.log("floor"+floor_id)
  var floor_div = document.getElementById("floor"+floor_id)
  console.log(estimate)

  if (estimate["estimate"] == null){
    floor_div.totalOccupants = "???"
  }else if (isNaN(parseInt(estimate["estimate"]["estimate"]))){
    console.log((isNaN(parseInt(estimate["estimate"]["estimate"]))))
    floor_div.totalOccupants = floor_div.totalOccupants
  }else{
    if (isNaN(floor_div.totalOccupants)){
      floor_div.totalOccupants = parseInt(estimate["estimate"]["estimate"])
    }else{
      floor_div.totalOccupants = floor_div.totalOccupants + parseInt(estimate["estimate"]["estimate"])
    }
  }

  oc = floor_div.totalOccupants
  if (oc == 0){
    floor_div.style.background = "white"
  }else if(oc <= 25) {
    floor_div.style.background = "seagreen"
  }else if(oc <= 50) {
    floor_div.style.background = "orange"
  }else if(oc <= 75) {
    floor_div.style.background = "orangered"
  }else if(oc > 75) {
    floor_div.style.background = "red"
  }else {
    floor_div.style.background = "grey"
  }


  floorNum = floor_div.childNodes[1]
  floorNum.childNodes[0].textContent = "Total: " + floor_div.totalOccupants
}

function handleEstimate(resp, floor_id){

  // Decode JSON
  data = JSON.parse(resp)
  addReport(data, floor_id)
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

  // New floor div
  var new_floor = document.createElement("div");
  new_floor.id = "floor"+floor["floor_id"]
  new_floor.className = "floor"
  new_floor.totalOccupants = "NULL"

  // Floor name
  var name_div = document.createElement("div")
  name_div.className = "floorName"
  var name = document.createElement("h1")
  var t_node = document.createTextNode(floor["floor_name"]);
  name.appendChild(t_node)
  name_div.appendChild(name)
  new_floor.appendChild(name_div)

  // Total number
  var num_div = document.createElement("div")
  num_div.className = "floorNum"
  var num = document.createElement("h1")
  var t_node = document.createTextNode("Total: ???");
  num.appendChild(t_node)
  num_div.appendChild(num)
  new_floor.appendChild(num_div)

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
