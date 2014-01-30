var markers = [];
var iterator = 0;
var geocoder;
var map;
var waypoints;
var longitude;
var latitude;
var location;
var coordinates = []

var city_latlong = [];

// Javascript to get waypoints for a movie
function getWaypoints(job1, job2) {
    //Clear the carts container
    $("#cards").empty()
    //Log inputs to console
    console.log(("Input is job1 = " + job1 + ", job2 = " + job2));
    //Go to the page /waypoints (see myapp.py) and pass in the arguments
    $.get('/waypoints?job1='+job1+'&job2='+job2, function(result) {
        //Log the output to console
        console.log("Output is = " + result);
        //Fill in the results that will go on the page
        //var parsedJson = $.getJSON(result)
        var parsedJson = eval(result);
        console.log(parsedJson);
        coordinates = []
        for (pair in parsedJson) {
            // add cards
            addCard(parsedJson[pair][pair], pair);
            coordinates.push({"Latitude": parsedJson[pair][pair][1],
                              "Longitude": parsedJson[pair][pair][2]})
        }
        console.log("Coordinates1 " + coordinates)
        // drop pins
        drop()
        //I don't think this returned value is used at all
        return result;
    });
};

function addCard(city,i) {
    $('#cards').append('<div class="card hovercard" id="card'+i+'">');
    $('#card'+i).prepend('<img id="theImg" src="'+city[3]+'"/>');
    $('#card'+i).append('<div class="info" id="info'+i+'">');
    $('#info'+i).append('<div class="title">' + city[0] +'</div');
    $('#info'+i).append('<div class="desc">'+city[4]+'</div>');
}

var sf = new google.maps.LatLng(37.7771187, -122.4196396);
var us = new google.maps.LatLng(37.0625,-95.677068);

function initialize(center) {
    geocoder = new google.maps.Geocoder();
    var mapOptions = {
        center: center,
        zoom: 4
    }
    map = new google.maps.Map(document.getElementById("map-canvas"), mapOptions);
}

function createMarkerlist(){
    for (pair in coordinates) {
        console.log("Latitude " + coordinates[pair]["Latitude"] + " Longitude " + coordinates[pair]["Longitude"])
        city_latlong.push(new google.maps.LatLng(coordinates[pair]["Latitude"], coordinates[pair]["Longitude"]))
    }
    console.log("Creating new Marker List")
}

function drop() {
    deleteMarkers()
    createMarkerlist()
    for (var i = 0; i < city_latlong.length; i++) {
        setTimeout(function() {
            addMarker(i);
        }, i * 200);
    }
}

function addMarker() {
    markers.push(new google.maps.Marker({
        position: city_latlong[iterator],
        map: map,
        draggable: false,
        animation: google.maps.Animation.DROP,
        title:"City #" + (parseInt(iterator+1))
    }));
    iterator++;
    console.log("Adding markers.")
}

function clearMarkers() {
    setAllMap(null);
    console.log("Clearing markers")
}

// Deletes all markers in the array by removing references to them.
function deleteMarkers() {
    clearMarkers();
    city_latlong = [];
    markers = [];
    iterator = 0;
    console.log("Deleting markers")
}

function setAllMap(map) {
    for (var i = 0; i < markers.length; i++) {
        markers[i].setMap(map);
    }
}
google.maps.event.addDomListener(window, 'load', initialize(us));
