
// Dom Elements
var buildingContainer = document.getElementById("buildings");

// Api Endpoints
var base_url = window.location.hostname
var buildings_url =  base_url + "/api/v1/buildings/get-all"
var building_page = base_url + "/webapp/building/"

var buildingImgDir = "../static/img/buildings/"

getBuildings()


function addBuilding(building){

  // New building div
  var new_building = document.createElement("div");
  new_building.id = "building"

  // Image div
  var img = document.createElement("img")
  img.id = "building_img"
  img.src= buildingImgDir + "default.jpg"
  img.width = 160
  img.height = 160
  new_building.appendChild(img)

  // Name para
  var name = document.createElement("p")
  var t_node = document.createTextNode(building["building_name"]);
  name.appendChild(t_node)
  new_building.appendChild(name)

  // Add link
  new_building.addEventListener('click', function(){
      window.location.href = building_page + building["building_id"]
  });

  // Add to box
  buildingContainer.appendChild(new_building)
}

function handleBuildings(resp){

  // Decode JSON
  data = JSON.parse(resp)
  buildings = data["buildings"]

  // Add each building
  for (building in buildings){
    addBuilding(buildings[building])
  }
}

function getBuildings(){
  url = buildings_url
  var xmlHttp = new XMLHttpRequest();
  xmlHttp.onreadystatechange = function() {
      if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
          handleBuildings(xmlHttp.responseText);
  }
  xmlHttp.open("GET", url, true); // true for asynchronous
  xmlHttp.send(null);
}
