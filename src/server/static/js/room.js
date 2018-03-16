
// Dom Elements
var roomContainer = document.getElementById("rooms");

// Api Endpoints
var base_url = window.location.hostname
var room_url = "/api/v1/rooms/get/"

var curr_url = window.location.href.split("/")
var room_id = curr_url.slice(-1)[0]

var room_name_div = document.getElementById("room_name")
var room_desc_div = document.getElementById("room_desc")

getRoomData(room_id)


function addRoomData(data){

  // room name
  var name = document.createElement("h1")
  var t_node = document.createTextNode(data[0]);
  name.appendChild(t_node)
  room_name_div.appendChild(name)

  // room desc
  var desc = document.createElement("p")
  var t_node = document.createTextNode(data[1]);
  desc.appendChild(t_node)
  room_desc_div.appendChild(desc)



}


function addEstimateData(data){

  console.log(data)
  // room curent estimate
  var desc = document.createElement("p" )
  if (data == []){
    var t_node = document.createTextNode("Current estimate: ???");
    desc.appendChild(t_node)
    room_desc_div.appendChild(desc)
    var desc = document.createElement("p" )
    var t_node = document.createTextNode("No info in last 24 hours.");
    desc.appendChild(t_node)
    room_desc_div.appendChild(desc)
    return
  }

  var t_node = document.createTextNode("Current estimate: " + data[0]["estimate"]);
  desc.appendChild(t_node)
  room_desc_div.appendChild(desc)
  var desc = document.createElement("p")
  e_time = new Date(0)
  e_time.setUTCSeconds(data[0]["time"])
  var t_node = document.createTextNode("Last report : " + e_time.toUTCString());
  desc.appendChild(t_node)
  room_desc_div.appendChild(desc)

  datap = []
  for (estimate in data){
    e_time = new Date(0)
    e_time.setUTCSeconds(data[estimate]["time"])
    datap.push({ "y": data[estimate]["estimate"], "x": e_time})
  }

  var chart = new CanvasJS.Chart("room_estimates", {
  	animationEnabled: true,
    zoomEnabled: true,
  	theme: "light2",
  	title:{
  		text: "Number of occupants"
  	},
  	axisY:{
  		includeZero: false
  	},
  	data: [{
  		type: "line",
  		dataPoints: datap
  	}]
  });
  chart.render();
}


function handleRoomData(resp){

  // Decode JSON
  data = JSON.parse(resp)

  room = data['room']
  estimates = data['estimates']

  addRoomData(room)
  addEstimateData(estimates)
}




function getRoomData(room_id){
  url = room_url + room_id
  var xmlHttp = new XMLHttpRequest();
  xmlHttp.onreadystatechange = function() {
      if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
          handleRoomData(xmlHttp.responseText);
  }
  xmlHttp.open("GET", url, true); // true for asynchronous
  xmlHttp.send(null);
}
