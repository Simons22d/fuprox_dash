var map;

function initMap() {
    var latitude = -1.2813573977664976; 
    var longitude = 36.81253115085258; 

    var myLatLng = { lat: latitude, lng: longitude };

    map = new google.maps.Map(document.getElementById('map'), {
        center: myLatLng,
        zoom: 15,
        disableDoubleClickZoom: true, // disable the default map zoom on double click
    });

    // Update lat/long value of div when anywhere in the map is clicked    
    google.maps.event.addListener(map, 'click', function (event) {
        let lat = event.latLng.lat();
        let long = event.latLng.lng();  
        document.getElementById('latclicked').innerHTML = event.latLng.lat();
        document.getElementById('longclicked').innerHTML = event.latLng.lng();
        // get the coordinate of the location on map and save it to the database
        geoCodeRequest(event.latLng.lat(),event.latLng.lng());
    });

    // Update lat/long value of div when you move the mouse over the map
    // google.maps.event.addListener(map, 'mousemove', function (event) {
    //     document.getElementById('latmoved').innerHTML = event.latLng.lat();
    //     document.getElementById('longmoved').innerHTML = event.latLng.lng();
    // });

    var marker = new google.maps.Marker({
        position: myLatLng,
        map: map,
        //title: 'Hello World'

        // setting latitude & longitude as title of the marker
        // title is shown when you hover over the marker
        title: latitude + ', ' + longitude
    });

    // Update lat/long value of div when the marker is clicked
    marker.addListener('click', function (event) {
        let lat = event.latLng.lat();
        let long = event.latLng.lng();  
        document.getElementById('latclicked').innerHTML = lat;
        document.getElementById('longclicked').innerHTML = long;
    });

    // Create new marker on double click event on the map
    google.maps.event.addListener(map, 'dblclick', function (event) {
        var marker = new google.maps.Marker({
            position: event.latLng,
            map: map,
            title: event.latLng.lat() + ', ' + event.latLng.lng()
        });

        // Update lat/long value of div when the marker is clicked
        marker.addListener('click', function () {
            document.getElementById('latclicked').innerHTML = event.latLng.lat();
            document.getElementById('longclicked').innerHTML = event.latLng.lng();
        });
    });

    // Create new marker on single click event on the map
    // google.maps.event.addListener(map,'click',function(event) {
    //     var marker = new google.maps.Marker({
    //       position: event.latLng, 
    //       map: map, 
    //       title: event.latLng.lat()+', '+event.latLng.lng()
    //     });                
    // });
}


const geoCodeRequest = (lat,long) =>{
    let key = "af236a4eb6f160";
    let locationData = geoCode(key,lat,long); 
    return locationData;
}

/*
address ....
https://eu1.locationiq.com/v1/reverse.php?key=YOUR_PRIVATE_TOKEN&lat=LATITUDE&lon=LONGITUDE&format=json
*/
const geoCode = (apiKey,lat,long) =>{
    $.ajax({
        url : `https://eu1.locationiq.com/v1/reverse.php?key=${apiKey}&lat=${lat}&lon=${long}&format=json`,
        method : "GET",
        beforeSend : ()=>{
            // show loading ... 
            console.log("loading ...")
        },
        success : (data) =>{
            console.log(data);
            $("#suggestLocation").val(data.display_name);
            $("#long").val(data.lon)
            $("#lat").val(data.lat);
        },
        error : (error)=>{
            console.log(error);
        }
    })
}