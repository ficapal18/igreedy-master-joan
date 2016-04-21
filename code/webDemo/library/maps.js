var markerCluster;
var markers = [];
var circlesMarker = [];
var circlesMeasurement = [];
var map;
var circleShowed = false;
var thresholdEmptyCircle=6371;
var center =  new google.maps.LatLng(48.6908333333, 9.14055555556);
var markerInTheCluster;
var data;
var mplaneCapability, mplaneSpecification, mplaneResult;
var dateMeasurement,functionFinished,functionFinished2;
var timestamps;
var timemaps=null;
var minmax=[];
var _min=0;
var _max=100;
var session_num=1;
var llindar=0.5
var hola;

//trick for wait until the data are downloaded
function waitForLoadingData() {
    if (typeof data === "undefined") {
        setTimeout(waitForLoadingData, 100);
    } else {
        reloadMarkers()
    }
}


function waitForLoadingData2() {
    if (typeof data === "undefined") {
        setTimeout(waitForLoadingData2, 100);
    } else {
        reloadMarkers()
    }
}

function test() {

                var timemaps;
            var h=setInterval(function () {

                //prova2()
                loadinfo1()

                //loadLocation()
            },1000);

}

function loadinfo1() {
    //////////////////////////////////////////////////////////////////window.alert("2")
        var data=undefined
        var timestamps=undefined
        var counts=undefined

    //window.alert("prva1")
    setTimeout(function() {
    var t = document.createElement('script');
    t.setAttribute('src', "data/anycastJson/" + document.getElementById("suggestBox").value.split("\t")[0]);    //setAttribute('src', "data/anycastJson/output.json");
    document.body.appendChild(t);
    }, 500);

    setTimeout(function() {
    var t = document.createElement('script');
    t.setAttribute('src', "data/anycastJson/timestamp.json");
    document.body.appendChild(t);
    }, 500);

    setTimeout(function() {
    var t = document.createElement('script');
    t.setAttribute('src', "data/anycastJson/outputs/number.json");
    document.body.appendChild(t);
    }, 500);
        ////////////////////////////////////////////////////////////////////window.alert("3")
        waitForLoadinggeneraldata()

}




function waitForLoadinggeneraldata() {

if ((typeof data === "undefined")  || (typeof timestamps === "undefined") || (typeof counts === "undefined")){
            //window.alert("joan3")
        setTimeout(waitForLoadinggeneraldata, 100);

    } else{


                if (timemaps === timestamps.timestamp) {
                ////////////////////////////////////////////////////////////////////////////////////////////////window.alert("fail")
                }else{

                       document.querySelector('#fadertime').max=counts.count;
                       document.querySelector('#volumetime').value = (counts.count+1)+"/"+(counts.count+1);
                       timemaps=timestamps.timestamp;
                       //////////////////////////////////////////////////////reloadMarkers()
                       loadLocation()

                }

    }

}


function initialize() {
    //****mPlane Message****\\
    mplaneCapability = 'mPlane Capability:\n{\"capability\": \"anycast-geolocation\",\n  \"version\": 1,\n  \"registry\": \"http://ict-mplane.eu/registry/core\",\n  \"when\": \"2015-03-25 13:05:50 ... future\",\n  \"parameters\": {\n"source.ip4\": \"127.0.0.1\",\n                 \"destination.ip4\": \"*\"},\n  \"results\": [\"anycast\",\n              \"anycastGeolocation\"]}'
    myTextArea = document.getElementById('mplaneMessage');
    myTextArea.innerHTML = mplaneCapability;
    //****mPlane Message****\\

    //****map option****\\
    map = new google.maps.Map(document.getElementById('map'), {
    zoom: 2,    
    minZoom: 2,
    center: center,
    mapTypeId: google.maps.MapTypeId.ROADMAP,
    zoomControlOptions: {
      style: google.maps.ZoomControlStyle.SMALL
    }
    });
    markerCluster = new MarkerClusterer(map, [], {
        minimumClusterSize: '6'
    });
    //****map option****\\

    manageToggle(); //initialise all the toggle variable

}

//real time measurement
function measure(){
     dateMeasurement="now";
     mplaneSpecification= '\n\nmPlane Specification:\n{\"capability\": \"anycast-geolocation\",\n  \"version\": 1,\n  \"registry\": \"http://ict-mplane.eu/registry/core\",\n  \"when\": \"now\",\n  \"parameters\": {\n"source.ip4\": \"127.0.0.1\",\n                 \"destination.ip4\": \"'+ document.getElementById("suggestBox").value.split("\t")[0]+'\"},\   \"results\": [\"anycast\",\n              \"anycastGeolocation\"]}'
     myTextArea.innerHTML+= mplaneSpecification;

    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (xhttp.readyState == 4 && xhttp.status == 200) {
          document.getElementById("suggestBox").value=xhttp.responseText;
          loadLocation();
        }
    }
    xhttp.open("GET", "http://127.0.0.1/?ip="+document.getElementById("suggestBox").value.split("\t")[0], true);
    xhttp.send();
    dateMeasurement=(new Date().toJSON().slice(0,10))+" "+(new Date().toJSON().slice(11,19))
}

//****mPlane Message****\\
//control for show only valid IP
function checkInput(){
    if( document.getElementById("suggestBox").value.split("\t")[0].split(".").length==4)
        return true;
}

function setSpecification(){
    if( checkInput()){
         dateMeasurement="2015-03-25 13:05:50"
         mplaneSpecification= '\n\nmPlane Specification:\n{\"specification\": \"anycast-geolocation\",\n  \"version\": 1,\n  \"registry\": \"http://ict-mplane.eu/registry/core\",\n   \"token\": \"ea839b56bc3f6004e95d780d7a64d899\",\n   \"when\": \"2015-03-25 13:05:50\",\n  \"parameters\": {\n"source.ip4\": \"127.0.0.1\",\n                 \"destination.ip4\": \"'+ document.getElementById("suggestBox").value.split("\t")[0]+'\"},\n  \"results\": [\"anycast\",\n              \"anycastGeolocation\"]}'
    myTextArea.innerHTML+= mplaneSpecification;
    }
}
//****mPlane Message****\\

function loadLocation() {

    functionFinished=false

    //reset variable
    /*
    //document.getElementById('reset10Ranking').selected = true;
    //document.getElementById('reset10Size').selected = true;
    //document.getElementById('resetPublicInfo').selected = true;
    //document.getElementById('resetGroundTruth').selected = true;
    */

   //document.getElementById('resetSelector').selected = true;
    document.getElementById('numberInstanceGT').innerHTML = "";
    data = undefined
    //resetMap
    //map.setCenter(center);
    //map.setZoom(2);
//TODO: try to clean
    circleShowed = true
    showCircles();

//-------------------------------
    circlesMarker = new Array()
    circlesMeasurement = []
//it wait 500ms, for read the right input(otherwise it will be empty the input)
    setTimeout(function() {
        var s = document.createElement('script');
        s.setAttribute('src', "data/anycastJson/" + document.getElementById("suggestBox").value.split("\t")[0]);
        document.body.appendChild(s);

    }, 500);

    waitForLoadingData()

//draw graphs after loaded the location
    drawLinesChart();
    drawPie('platformPie', dataPlatforms);
    drawPie('countryPie', dataCountry);

}



function reloadMarkerscheck() {


    circlesMarker = new Array()
    anycastResult="True"
    if (data.count<2)
        anycastResult="False"

    mplaneResult= '\n\nmPlane Result:\n{\"result\": \"anycast-geolocation\",\n  \"version\": 1,\n  \"registry\": \"http://ict-mplane.eu/registry/core\",\n   \"token": "ea839b56bc3f6004e95d780d7a64d899\",   \n\"when\": \"'+dateMeasurement+'\",\n  \"parameters\": {\n"source.ip4\": \"127.0.0.1\",\n                 \"destination.ip4\": \"'+ document.getElementById("suggestBox").value.split("\t")[0].split("-")[0]+'\"},\n  \"results\": [\"anycast\",\n              \"anycastGeolocation\"]\n   \"resultvalues\": [\"'+anycastResult+'\", \"'+JSON.stringify(data)+'\"]}'
        myTextArea.innerHTML+= mplaneResult;

    document.getElementById('numberInstance').innerHTML = "Number of instances: " + data.count
    document.getElementById('hitToggle').checked=false;
    showMarkersHit()

    // Reset the markers array
    markers = [];
    heatData=[];

    //Read the new markers
    for (var i = 0; i < data.count; i++) {
        var markerData = data.instances[i].marker;
//------------HEATMAPTOFIX---------------
        var lat=parseFloat(markerData.latitude)+(Math.random() * (0.0250) + 0.14200);
        var lng=parseFloat(markerData.longitude)+(Math.random() * (0.0250) + 0.14200); //TODO: change
        //alert(markerData.longitude.toString()+"  "+lng.toString()+"  "+(Math.random() * (0.0150) + 2.54200))
        heatData[i] = new google.maps.LatLng(lat,lng);
//------------HEATMAPTOFIX---------------

        var latLng = new google.maps.LatLng(lat,lng);

        var marker = new google.maps.Marker({
            position: latLng,
            title: markerData.id+"<br />City:"+markerData.city+"<br />Country:"+markerData.code_country,
            icon: "http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=H|00FF00|000000"
        });

        var circleData = data.instances[i].circle;

        var drawCircle = new google.maps.Circle({
            center: new google.maps.LatLng(circleData.latitude, circleData.longitude),
            radius: circleData.radius * 1000, // metres
            strokeColor: '#FF0000',
            strokeOpacity: 0.8,
            strokeWeight: 2,
            fillColor: '#FF0000',
            fillOpacity: 0.35,
        });

        google.maps.event.addListener(marker, 'click', function() {
            var infowindow = new google.maps.InfoWindow({
        content: "<p>" + "Iata: " + this.getTitle() + "<br />Latitude: " + this.getPosition().lat().toFixed(5) + "<br />Longitude: " + this.getPosition().lng().toFixed(5)
            });
            infowindow.open(map, this);
        });
        <!-- end draw circle-->
        markers.push(marker);
        circlesMarker.push(drawCircle)

        }

    //read the all the empty circle

    for (var i = 0; i < data.countAllCircles; i++) {
        var circleData = data.allCircles[i];
        if(parseFloat(circleData.radius)<thresholdEmptyCircle){
        var drawCircle = new google.maps.Circle({
            center: new google.maps.LatLng(circleData.latitude, circleData.longitude),
            radius: circleData.radius * 1000, // metres
            strokeColor: '#FF0000',
            strokeOpacity: 0.2,
            strokeWeight: 2,
            fillColor: '#FF0000',
            fillOpacity: 0.00,
        });
        circlesMarker.push(drawCircle)
        }
        }

    manageToggle('initialize')

    //Add the new marker to the cluster
    if(document.getElementById('cluster').checked)
        {markerCluster.addMarkers(markers) }//it should check before}
    functionFinished=true
}



//////////////////////



function reloadMarkers() {
    circlesMarker = new Array()
    anycastResult="True"
    if (data.count<2)
        anycastResult="False"

    mplaneResult= '\n\nmPlane Result:\n{\"result\": \"anycast-geolocation\",\n  \"version\": 1,\n  \"registry\": \"http://ict-mplane.eu/registry/core\",\n   \"token": "ea839b56bc3f6004e95d780d7a64d899\",   \n\"when\": \"'+dateMeasurement+'\",\n  \"parameters\": {\n"source.ip4\": \"127.0.0.1\",\n                 \"destination.ip4\": \"'+ document.getElementById("suggestBox").value.split("\t")[0].split("-")[0]+'\"},\n  \"results\": [\"anycast\",\n              \"anycastGeolocation\"]\n   \"resultvalues\": [\"'+anycastResult+'\", \"'+JSON.stringify(data)+'\"]}'
        myTextArea.innerHTML+= mplaneResult;

    document.getElementById('numberInstance').innerHTML = "Number of instances: " + data.count
    document.getElementById('hitToggle').checked=false;
    showMarkersHit()

    // Reset the markers array
    markers = [];
    heatData=[];



    //Read the new markers
    for (var i = 0; i < data.count; i++) {

        var markerData = data.instances[i].marker;
//------------HEATMAPTOFIX---------------
        var lat=parseFloat(markerData.latitude)+(Math.random() * (0.0250) + 0.14200);
        var lng=parseFloat(markerData.longitude)+(Math.random() * (0.0250) + 0.14200); //TODO: change
        //alert(markerData.longitude.toString()+"  "+lng.toString()+"  "+(Math.random() * (0.0150) + 2.54200))
        heatData[i] = new google.maps.LatLng(lat,lng);
//------------HEATMAPTOFIX---------------
        
        var latLng = new google.maps.LatLng(lat,lng);

        var marker = new google.maps.Marker({
            position: latLng,
            title: markerData.id+"<br />City:"+markerData.city+"<br />Country:"+markerData.code_country,
            icon: "http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=H|00FF00|000000"
        });
 
        var circleData = data.instances[i].circle;

        var drawCircle = new google.maps.Circle({
            center: new google.maps.LatLng(circleData.latitude, circleData.longitude),
            radius: circleData.radius * 1000, // metres
            strokeColor: '#FF0000',
            strokeOpacity: 0.8,
            strokeWeight: 2,
            fillColor: '#FF0000',
            fillOpacity: 0.35,
        });

        google.maps.event.addListener(marker, 'click', function() {
            var infowindow = new google.maps.InfoWindow({
        content: "<p>" + "Iata: " + this.getTitle() + "<br />Latitude: " + this.getPosition().lat().toFixed(5) + "<br />Longitude: " + this.getPosition().lng().toFixed(5)
            });
            infowindow.open(map, this);
        });
        <!-- end draw circle-->
        markers.push(marker);
        circlesMarker.push(drawCircle)

        }

        /////////////////////joan
        circlestime=[];
        for (var i = 0; i < data.countAllCircles; i++) {

        circlestime.push(data.allCircles[i].timestamp)
                //window.alert(circlestime[i])
        }
        /*
        var max=getMaxOfArray(circlestime);
        var min=getMinOfArray(circlestime)
        thresholdTimereal=(thresholdTime*(max-min)/100)+min;
        thresholdTimereal2=(thresholdTime2*(max-min)/100)+min;
         && (circleData.timestamp<thresholdTimereal) && (circleData.timestamp>thresholdTimereal2))*/

        /*
        window.alert(thresholdTime)
        window.alert(max)
        window.alert(thresholdTimereal)
        window.alert(min)
        */


    //read the all the empty circle
                    //window.alert("limit "+thresholdTimereal)
    for (var i = 0; i < data.countAllCircles; i++) {
    /////////////////////joan

        var circleData = data.allCircles[i];

        if(parseFloat(circleData.radius)<thresholdEmptyCircle){

        hola=hola+1;
        var drawCircle = new google.maps.Circle({
            center: new google.maps.LatLng(circleData.latitude, circleData.longitude),
            radius: circleData.radius * 1000, // metres
            strokeColor: '#FF0000',
            strokeOpacity: 0.2,
            strokeWeight: 2,
            fillColor: '#FF0000',
            fillOpacity: 0.00,
        });
        circlesMarker.push(drawCircle)
        }
        }

    manageToggle('initialize')

    //Add the new marker to the cluster
    if(document.getElementById('cluster').checked)
        {markerCluster.addMarkers(markers) }//it should check before}
    functionFinished=true
}

function getMaxOfArray(numArray) {
  return Math.max.apply(null, numArray);
}
function getMinOfArray(numArray) {
  return Math.min.apply(null, numArray);
}

  
function updateEmptyCircle(threshold){
    document.querySelector('#volume').value = threshold+" km";
    thresholdEmptyCircle=threshold;
}
function updateEmptyCircle2(threshold){
    document.querySelector('#volume').value = threshold+" km";
    thresholdEmptyCircle=threshold;
    loadLocation()
    waitForLoadLocation()
}
/*
function updateEmptyCircle3(threshold){
   // window.alert(threshold)
    document.querySelector('#volume2').value = threshold+" %";
    thresholdTime=threshold;
    loadLocation()



}
*/function updateEmptyCircle3(t1){
   // window.alert(threshold)
//window.alert(t1)
    functionFinished2=false
    session_num=counts.count;
    document.querySelector('#volumetime').value = t1.toString()+"/"+session_num.toString();


    //window.alert(session_num)
    llindar=t1
    //Math.floor((session_num*t1)/100);

    document.querySelector('#suggestBox').value="./outputs/output"+llindar.toString()+".json"
                           document.querySelector('#fadertime').max=session_num;
    //document.querySelector('#session_number_html').value = "Actualization Number: "+llindar.toString()+"/"+session_num.toString();
   ////////////////////////////////////////////////////////////////////////////////////////// window.alert(document.querySelector('#suggestBox').value)

    functionFinished2=true


    //window.alert("data/anycastJson/outputs/output"+llindar.toString()+".json")

    //llindar=0;
    //window.alert(t1/100)
    //window.alert(llindar)
    //window.alert(conta_total*thresholdTime/100)
    //loadLocation()
    waitForLoadsuggestBox()
    //window.alert(document.querySelector('#suggestBox').value)

// window.alert(threshold)

}




//trick for wait until the data are downloaded
function waitForLoadLocation() {
    if (functionFinished == false) {
        setTimeout(waitForLoadLocation, 100);
    } else {
        checkToggle('circlesToggle')
    }
}

//trick for wait until the data are downloaded
function waitForLoadsuggestBox() {
    if (document.querySelector('#suggestBox').value != "./outputs/output"+llindar.toString()+".json") {
        setTimeout(waitForLoadsuggestBox, 50);
    } else {

        loadLocation()
    }
}

google.maps.event.addDomListener(window, 'load', initialize);
