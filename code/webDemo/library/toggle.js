var markersProbes = [],
    markersGT = [],
    gt = null,
    hit = null,
    miss = null,
    probes = null,
    circles = null,
    map, 
    pointarray, 
    heatmap,
    mplane=false;

function manageMplaneMessage(){

    if (String(toggleType) === "custom") {
        toggleSection.style.display = 'block';
    }

}
function manageToggle(toggleType) {

    gt = document.getElementById('GTToggle');
    hit = document.getElementById('hitToggle');
    miss = document.getElementById('missToggle');
    fp = document.getElementById('fpToggle');
    probes = document.getElementById('probesToogle');
    circles = document.getElementById('circlesToggle');
    cluster = document.getElementById('cluster');
    heat = document.getElementById('heatmap');
    toggleSection=document.getElementById('toggleSection')

/*
    if (String(toggleType) === "reset") {
        uncheckToggle('GTToggle', markersGT)
        uncheckToggle('probesToogle', markersProbes)
        hit.checked = true;
        miss.checked = false;
        fp.checked = false;
        if (circles.checked) {
            circles.click()
        }
        if (!cluster.checked) {
            cluster.click()
        }
    } else 
*/

   if (String(toggleType) === "initialize") {

        reloadToogle('GTToggle', markersGT)
        reloadToogle('probesToogle', markersProbes)
        reloadCircle()
        cleanHeatmap()
        heat.checked = false;
        hit.checked = true;
        cluster.checked = true;
        miss.checked = false;
        fp.checked = false;
//manage circle!
    //basic
    } else if (String(toggleType) === "1") {
        //toggleSection.style.display = 'none';

        //checkToggle('GTToggle');
        checkToggle('hitToggle');
        uncheckToggle('probesToogle', markersProbes)
        uncheckToggle('GTToggle', markersGT)
        miss.checked = false;
        fp.checked = false;
        if (circles.checked) {
            circles.click();
        }
    } else if (String(toggleType) === "2") {
        //extended
        //toggleSection.style.display = 'none';
        //checkToggle('GTToggle');
        checkToggle('hitToggle');
        //checkToggle('missToggle');
        //checkToggle('fpToggle');
        //uncheckToggle('probesToogle', markersProbes)
        uncheckToggle('GTToggle', markersGT)
        checkToggle('probesToogle', markersProbes)
        checkToggle('circlesToggle');
    } else if (String(toggleType) === "3") {
        //everything
        //toggleSection.style.display = 'none';
        checkToggle('GTToggle');
        checkToggle('hitToggle');
        checkToggle('missToggle');
        checkToggle('fpToggle');
        checkToggle('probesToogle');
        checkToggle('circlesToggle');

    } else if (String(toggleType) === "custom") {
        toggleSection.style.display = 'block';
    }
}


function checkToggle(toggle) {
    if (!document.getElementById(toggle).checked) {
        document.getElementById(toggle).click();
    }
}

function uncheckToggle(toggle, markersDisable) {
    if (document.getElementById(toggle).checked) {
        document.getElementById(toggle).checked = false;
        clearMapsFromMarkers(markersDisable)
    }
}

function reloadToogle(toggle,markersDisable){
    var checked=document.getElementById(toggle).checked
    uncheckToggle(toggle, markersDisable)
    if(checked){
        checkToggle(toggle);
   }
}
function reloadCircle(){ //to check
    var checked=circles.checked
    if(checked){
        showCircles();
   }
}

function cleanHeatmap(){
    heat.checked=false;
    if(heatmap!=null)
    {enableDisableHeatmap()}
}

//try to see how much effort for insert the gadget
function showMarkersProbes() {
    var usedProbes=[]

    if (probes.checked) {
        //probes in the solution
        for (var i = 0; i < data.count; i++) {
            var markerData = data.instances[i].circle;
            usedProbes.push(markerData.id)
            var latLng = new google.maps.LatLng(markerData.latitude,
                markerData.longitude);
            var marker = new google.maps.Marker({
                position: latLng,
                title: markerData.id,
                icon: "data/dot2.png",
                map: map
            });
            google.maps.event.addListener(marker, 'click', function() {
                    if(this.getTitle() % 1 === 0) {//if the title is a number is a Ripe Probe(try to change)
                        content="<p>" + "Probe: " + this.getTitle() + "<br />Latitude: " + this.getPosition().lat().toFixed(5) + "<br />Longitude: " +
 this.getPosition().lng().toFixed(5)+"<p>" + "<a href=\"https://atlas.ripe.net/probes/"+this.getTitle()+"\" target=\"_blank\">Ripe information</a>" 
                    }else{
                        content="<p>" + "Probe: " + this.getTitle() + "<br />Latitude: " + this.getPosition().lat().toFixed(5) + "<br />Longitude: " +
 this.getPosition().lng().toFixed(5)+"<p> "+ "<a href=\"http://dnsquery.org/ip2location/"+this.getTitle()+"\" target=\"_blank\">PlanetLab information</a>" 
                    }

                var infowindow = new google.maps.InfoWindow({
content: content
                });
                infowindow.open(map, this);
            });
            markersProbes.push(marker);
        }
        //probes used in the measurement
        /*
        for (var i = 0; i < allProbes.count; i++) {
            var markerData = allProbes.instances[i];
            if(usedProbes.indexOf(markerData.id) < 0){
                var latLng = new google.maps.LatLng(markerData.latitude,
                    markerData.longitude);
                var marker = new google.maps.Marker({
                    position: latLng,
                    title: markerData.id,
                    icon: "data/dotGrey.png",
                    map: map
                });
                google.maps.event.addListener(marker, 'click', function() {
                    var infowindow = new google.maps.InfoWindow({
                        content: "<p>" + "Probe: " + this.getTitle() + "<br />Latitude: " + this.getPosition().lat().toFixed(5) + "<br />Longitude: " + this.getPosition().lng().toFixed(5)+"<p>" 
                    });
                    infowindow.open(map, this);
                });
                markersProbes.push(marker);
            }
        }*/


        for (var i = 0; i < data.countAllCircles; i++) {
            var markerData =data.allCircles[i];
            if(usedProbes.indexOf(markerData.id) < 0 && (parseFloat(markerData.radius)<thresholdEmptyCircle  ||  thresholdEmptyCircle>6300) ){
                var latLng = new google.maps.LatLng(markerData.latitude,
                    markerData.longitude);
                var marker = new google.maps.Marker({
                    position: latLng,
                    title: markerData.id,
                    icon: "data/dotGrey.png",
                    map: map
                });
                google.maps.event.addListener(marker, 'click', function() {
                                      if(this.getTitle() % 1 === 0) {//if the title is a number is a Ripe Probe(try to change)
                        content="<p>" + "Probe: " + this.getTitle() + "<br />Latitude: " + this.getPosition().lat().toFixed(5) + "<br />Longitude: " +
 this.getPosition().lng().toFixed(5)+"<p>" + "<a href=\"https://atlas.ripe.net/probes/"+this.getTitle()+"\" target=\"_blank\">Ripe information</a>" 
                    }else{
                        content="<p>" + "Probe: " + this.getTitle() + "<br />Latitude: " + this.getPosition().lat().toFixed(5) + "<br />Longitude: " +
 this.getPosition().lng().toFixed(5)+"<p> "+ "<a href=\"http://dnsquery.org/ip2location/"+this.getTitle()+"\" target=\"_blank\">PlanetLab information</a>" 
                    }

                var infowindow = new google.maps.InfoWindow({
content: content
                });

                    infowindow.open(map, this);
                });
                markersProbes.push(marker);
            }
    }
    } else {
        probes.checked = true;
        uncheckToggle('probesToogle', markersProbes)

    }
}


function showMarkersHit() {
    if (hit.checked) {
        // default enable marker and cluster 
         markerCluster.addMarkers(markers)
        cluster.checked = true
    } else {
       // hide the marker and the cluster 
        for (var i = 0; i < markers.length; i++) {
            markers[i].setOptions({
                map: null,
                visible: true
            });
        }
        markerCluster.clearMarkers();
        cluster.checked = false
    }

}

function showMarkersGT() {
    if (gt.checked) {
        //Read the new markers
        document.getElementById('numberInstanceGT').innerHTML = "Number of GT: " + data.countGT;
        for (var i = 0; i < data.countGT; i++) {

            var markerData = data.markerGT[i];
            //var lat=parseFloat(markerData.latitude+(Math.random() * (0.1150 - 0.00200) + 0.08200).toFixed(5));
            //var lng=parseFloat(markerData.longitude+(Math.random() * (0.1150 - 0.00200) + 0.08200).toFixed(5)); //TODO: change
            var latLng = new google.maps.LatLng(markerData.latitude,markerData.longitude);
            var marker = new google.maps.Marker({
                position: latLng,
                title: markerData.id+"<br />City:"+markerData.city,
                icon: "http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=G|8B52CC|000000",
                map: map
            });

            google.maps.event.addListener(marker, 'click', function() {
                var infowindow = new google.maps.InfoWindow({
                    content: "<p>" + "Iata: " + this.getTitle() + "<br />Latitude: " + this.getPosition().lat().toFixed(5) + "<br />Longitude: " + this.getPosition().lng().toFixed(5)
                });
                infowindow.open(map, this);
            });
            markersGT.push(marker);
        }
    } else {
        document.getElementById('numberInstanceGT').innerHTML = "";
        gt.checked = true;
        uncheckToggle('GTToggle', markersGT)
    }
}


function clearMapsFromMarkers(markersArray) {
    for (var i = 0; i < markersArray.length; i++) {
        markersArray[i].setMap(null);
    }
    markersArray.length = 0;
}

function enableDisableHeatmap() {  
//DR: inspired from https://developers.google.com/maps/documentation/javascript/examples/layer-heatmap
    if (heat.checked) {
        if(cluster.checked){
            hit.click();
        }
        var pointArray = new google.maps.MVCArray(heatData);
        heatmap = new google.maps.visualization.HeatmapLayer({ 
            data: pointArray, 
            radius: 45,
            map: map 
            });
    } else {
        heatmap.setMap(null);
    }
}

function enableDisableCluster() {
    if (cluster.checked) {
        hit.checked = true;
        markerCluster = new MarkerClusterer(map, markers, {
            minimumClusterSize: '3'
        });
    } else {
        markerCluster.clearMarkers();
        for (var i = 0; i < markers.length; i++) {
            markers[i].setOptions({
                map: map,
                visible: true
            });
        }
    }
}

function resetCircles(){
for (var i = 0; i < circlesMarker.length; i++) {
    circlesMarker[i].setMap(null);
    circlesMarker[i].setVisible(false)
    }

}
function showCircles() {
    if (circleShowed == false) {
        for (var i = 0; i < circlesMarker.length; i++) {
            circlesMarker[i].setMap(map);
            circlesMarker[i].setVisible(true)
        }
        circleShowed = true
    } else {
        circleShowed = false
        for (var i = 0; i < circlesMarker.length; i++) {
            circlesMarker[i].setVisible(false)
        }
    }
}


function showMplaneMessage(){

    if (mplane == false) {
        document.getElementById('mplaneMessage').style.display = 'inline-block';
        document.getElementById('map-container').style.width= '70%';
        mplane = true
    } else {
        mplane = false
        document.getElementById('mplaneMessage').style.display = 'none';
        document.getElementById('map-container').style.width='100%';
        }
    
}
