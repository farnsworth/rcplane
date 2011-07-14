var poly;
var map;
var lengthDiv;
var selectedItem;
var intSelectedItem;
var markerArray = new Array();
    
var image = new google.maps.MarkerImage("images/marker.png",
	new google.maps.Size(18, 18),
	new google.maps.Point(0,0),
	new google.maps.Point(9, 9));
var imageSel = new google.maps.MarkerImage("images/marker_yellow.png",
	new google.maps.Size(18, 18),
	new google.maps.Point(0,0),
	new google.maps.Point(9, 9));


//Initialize map, poly
function initialize() {
	
    var myOptions = {
		zoom: 18,
		center: new google.maps.LatLng(45.650082, 13.767774),
    	disableDefaultUI: false,
    	mapTypeId: google.maps.MapTypeId.SATELLITE,
    	streetViewControl: false
    	}
    map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);

    var polyOptions = {
		strokeColor: '#000000',
		strokeOpacity: 1.0,
		strokeWeight: 2
    	}
    poly = new google.maps.Polyline(polyOptions);
    poly.setMap(map);
    
    
    lengthDiv = document.getElementById("length")
    map.controls[google.maps.ControlPosition.RIGHT_TOP].push(lengthDiv);
    updateLength()
    
    // Add a listener for the click event
    google.maps.event.addDomListener(map, 'click', function (e){addLatLng(e.latLng)});
    
}


//Add a new latLng to poly
function addLatLng(latLng) {
	var path = poly.getPath();
    //path.push(latLng);
    
    index = getIndexFromMarker(selectedItem)
    path.insertAt(index+1,latLng)
      
    var m = new google.maps.Marker({
		position: latLng,
	//	title: '#' + (path.getLength()-1),
		map: map,
		icon: imageSel,
		draggable : true,
		clickable : true
	});
	
	
	markerArray.splice(index+1,0, m)
	//markerArray.push(m);
	
    selectItem(m);
    //alert(getIndexFromMarker(selectedItem))
    google.maps.event.addDomListener(m, 'click', function(){selectItem(m);}  );
    google.maps.event.addDomListener(m, 'dragstart', function(e){selectItem(m);intSelectedItem = getIndexFromMarker(m);});
    google.maps.event.addDomListener(m, 'drag', function(e){changePath(m,e);});
    
    updateLength()    
}

function changePath(m,e){
	if (intSelectedItem >= 0)
		var path = poly.getPath();
		path.setAt(intSelectedItem, e.latLng);
		updateLength()
}

function getPoly(){
	return poly.getPath().getArray();
}


function getIndexFromMarker(m){
	var l = markerArray.length;
	if (l > 0) {
		var i = 0;
		while (markerArray[i] != m ){
			i = i+1;
			if (i==l) return -1;
		}
		return i;
	}
	else return -1;
}


function getSelectedItem(){
	return getIndexFromMarker(selectedItem);	
}

function selectItem(item){
	if (typeof(selectedItem) != "undefined")
		selectedItem.setIcon(image);
	item.setIcon(imageSel);
	selectedItem = item;
}
    
function selectItemFromInt(item){
	var m = markerArray[item];
	selectItem(m);
}

function removeItem(item){
	var index = getIndexFromMarker(item);
	markerArray.splice(index,1);
	item.setMap(null);
	delete item;
	var path = poly.getPath();
	path.removeAt(index);
	updateLength()
	//selectItemFromInt(markerArray.length-1)
}

function removeItemFromInt(index){
	item = markerArray[index]
	markerArray.splice(index,1);
	item.setMap(null);
	delete item;
	var path = poly.getPath();
	path.removeAt(index);
	updateLength()
	//selectItemFromInt(markerArray.length-1)
}

function keyboardEvent(e){
	var unicode=e.keyCode? e.keyCode : e.charCode;
	if (unicode==8){
		if (typeof(selectedItem) != "undefined")
			removeItem(selectedItem);
			selectedItem = undefined
	}
}

function clearAll(){
	while (markerArray.length > 0){
		removeItemFromInt(markerArray.length-1)
	}
}

function updateLength(){
	var path = poly.getPath();
	l = google.maps.geometry.spherical.computeLength(path);
	lengthDiv.innerHTML="Length: "+l.toFixed(1)+" m"
}

document.onkeypress = keyboardEvent;
