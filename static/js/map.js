(function () {
  var mapElement = document.getElementById("parcels-map-container");
  if (!mapElement) return;

  var map = L.map("parcels-map-container").setView([48.5, 10], 5);

  L.tileLayer(
    "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    { attribution: "Tiles &copy; Esri", maxZoom: 19 }
  ).addTo(map);

  var marker = null;

  function placeMarker(lat, lon) {
    if (marker) {
      marker.setLatLng([lat, lon]);
    } else {
      marker = L.marker([lat, lon]).addTo(map);
    }
    document.getElementById("parcels-lat").value = lat;
    document.getElementById("parcels-lon").value = lon;
  }

  map.on("click", function (event) {
    var lat = event.latlng.lat;
    var lon = event.latlng.lng;
    placeMarker(lat, lon);
    map.setView([lat, lon], Math.max(map.getZoom(), 15));
  });

  document.body.addEventListener("htmx:afterSwap", function (event) {
    var dataEl = event.detail.target.querySelector("#parcels-geocode-data");
    if (!dataEl) return;
    var lat = parseFloat(dataEl.dataset.lat);
    var lon = parseFloat(dataEl.dataset.lon);
    placeMarker(lat, lon);
    map.setView([lat, lon], 17);
  });
})();
