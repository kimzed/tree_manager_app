(function () {
  var mapElement = document.getElementById("parcels-map-container");
  if (!mapElement) return;

  var map = L.map("parcels-map-container").setView([48.5, 10], 5);

  L.tileLayer(
    "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    { attribution: "Tiles &copy; Esri", maxZoom: 19 }
  ).addTo(map);

  // View-only mode: display polygon without draw controls
  if (mapElement.dataset.viewOnly === "true") {
    var viewPolygon = mapElement.dataset.polygon;
    if (viewPolygon && viewPolygon !== "null") {
      var displayLayer = L.geoJSON(JSON.parse(viewPolygon));
      displayLayer.addTo(map);
      map.fitBounds(displayLayer.getBounds());
    }
    return;
  }

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

  // Section 3: leaflet-draw polygon drawing
  var drawnItems = new L.FeatureGroup();
  map.addLayer(drawnItems);

  function createDrawControl() {
    return new L.Control.Draw({
      draw: {
        polygon: true,
        polyline: false,
        rectangle: false,
        circle: false,
        marker: false,
        circlemarker: false,
      },
      edit: { featureGroup: drawnItems },
    });
  }

  var drawControl = createDrawControl();
  map.addControl(drawControl);

  function updatePolygonUI(layer) {
    var latlngs = layer.getLatLngs()[0];
    var area = L.GeometryUtil.geodesicArea(latlngs);
    var geojson = layer.toGeoJSON().geometry;

    document.getElementById("parcels-polygon").value = JSON.stringify(geojson);
    document.getElementById("parcels-area").value = area.toFixed(2);
    document.getElementById("parcels-area-display").textContent =
      Math.round(area) + " m²";
    document.getElementById("parcels-area-display").classList.remove("hidden");
    document.getElementById("parcels-save-btn").classList.remove("hidden");
    document.getElementById("parcels-clear-btn").classList.remove("hidden");
    var nameInput = document.getElementById("parcels-name-input");
    if (nameInput) nameInput.classList.remove("hidden");
  }

  map.on(L.Draw.Event.CREATED, function (event) {
    drawnItems.clearLayers();
    map.removeControl(drawControl);
    drawControl = createDrawControl();
    map.addControl(drawControl);
    drawnItems.addLayer(event.layer);
    var resultEl = document.getElementById("parcels-save-result") || document.getElementById("parcels-update-result");
    if (resultEl) resultEl.innerHTML = "";
    updatePolygonUI(event.layer);
  });

  map.on(L.Draw.Event.EDITED, function (event) {
    event.layers.eachLayer(function (layer) {
      updatePolygonUI(layer);
    });
  });

  map.on(L.Draw.Event.DELETED, function () {
    clearPolygon();
  });

  function clearPolygon() {
    drawnItems.clearLayers();
    map.removeControl(drawControl);
    drawControl = createDrawControl();
    map.addControl(drawControl);
    document.getElementById("parcels-polygon").value = "";
    document.getElementById("parcels-area").value = "";
    document.getElementById("parcels-area-display").classList.add("hidden");
    document.getElementById("parcels-save-btn").classList.add("hidden");
    document.getElementById("parcels-clear-btn").classList.add("hidden");
    var nameInput = document.getElementById("parcels-name-input");
    if (nameInput) nameInput.classList.add("hidden");
    var resultEl = document.getElementById("parcels-save-result") || document.getElementById("parcels-update-result");
    if (resultEl) resultEl.innerHTML = "";
  }

  // Section 4: Clear button click handler
  var clearBtn = document.getElementById("parcels-clear-btn");
  if (clearBtn) {
    clearBtn.addEventListener("click", function () {
      clearPolygon();
    });
  }

  // Hide save button after successful save to prevent duplicates
  document.body.addEventListener("htmx:afterSwap", function (event) {
    var targetId = event.detail.target.id;
    if (
      (targetId === "parcels-save-result" || targetId === "parcels-update-result") &&
      event.detail.target.querySelector(".alert-success")
    ) {
      document.getElementById("parcels-save-btn").classList.add("hidden");
    }
  });

  // Section 5: Edit mode — load existing polygon from data attribute
  function initEditMode(geojsonData) {
    if (!geojsonData) return;

    var layer = L.geoJSON(geojsonData).getLayers()[0];
    drawnItems.addLayer(layer);
    map.fitBounds(layer.getBounds());
    updatePolygonUI(layer);
  }

  var existingPolygon = mapElement.dataset.polygon;
  if (existingPolygon && existingPolygon !== "null") {
    initEditMode(JSON.parse(existingPolygon));
  }
})();
