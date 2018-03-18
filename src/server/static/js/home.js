
// Dom Elements
var buildingContainer = document.getElementById("buildings");

// Api Endpoints
var base_url = window.location.hostname
var buildings_url =  "/api/v1/buildings/get-all"
var building_page = "/webapp/building/"

var buildingImgDir = "../static/img/buildings/"

getBuildings()


function addBuilding(building){

  // New building div
  var new_building = document.createElement("div");
  new_building.className = "building"

  // Image div
  var img = document.createElement("div")
  img.className = "building_img"
  var imgi = document.createElement("img")
  imgi.src= buildingImgDir + "default.jpg"
  img.appendChild(imgi)
  new_building.appendChild(img)

  // Name
  var named = document.createElement("div")
  named.className = "building_info"
  var name = document.createElement("h2")
  var t_node = document.createTextNode(building["building_name"]);
  name.appendChild(t_node)
  named.append(name)
  new_building.appendChild(named)

  // Description
  var descd = document.createElement("div")
  descd.className = "building_info"
  var desc = document.createElement("p")
  var t_node = document.createTextNode(building["building_desc"]);
  desc.appendChild(t_node)
  descd.append(desc)
  new_building.appendChild(descd)




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
