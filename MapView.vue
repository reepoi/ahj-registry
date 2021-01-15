<template>
  <div class="ahj-public-list-container">
    <div id="mapdiv">
      <ahj-search-filter></ahj-search-filter >
    </div>
  </div>
</template>

<script>
import L from "leaflet";
import constants from '../constants.js';
import AHJSearchPageFilter from "./AHJSearchPageFilter.vue";
export default {
 components: {
    'ahj-search-filter': AHJSearchPageFilter
 },
 name: "Map",
 data() {
   return{
     leafletMap: null,
     polygons: null,
     polygonLayer: null,
     currSearchMarker: null,
     markerLayerGroup: null,
     currSelectedMarker: null,
     markerColors: ['lightblue', 'blue', 'darkblue']
   }
 },
 methods: {
   /*
    * Initialize the leaflet map and set it as the store's leaflet map
    */
   setupLeafletMap() {
    let leafletMap = L.map('mapdiv', {zoomControl: false}).setView(this.$store.state.mapViewCenter, 5);
    L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
    maxZoom: 18,
    id: 'mapbox/streets-v11',
    tileSize: 512,
    zoomOffset: -1,
    accessToken: 
    }).addTo(leafletMap);
    
    this.leafletMap = leafletMap;
    this.markerLayerGroup = L.layerGroup().addTo(this.leafletMap);
    this.$store.commit("setLeafletMap", leafletMap);
   },
   // Replace map's existing polygons and markers with ones from the new search
   updateMap(){
      this.markerLayerGroup.clearLayers();
      this.addPolygonLayer();
      this.updateMapMarkers();
   },
   // Add all AHJ jurisdiction polygons to map
   addPolygonLayer() {
     // Clear existing polygons if any
    if(this.polygonLayer !== null){
        this.polygonLayer.removeFrom(this.leafletMap);
    }
    this.polygons = this.$store.state.callData
                        .map(ahj => ahj.mpoly)
                        .filter(mpoly => mpoly !== null)
                        .sort((a, b) => a.properties.ALAND - b.properties.ALAND);
    this.polygonLayer = L.geoJSON(this.polygons, {
      style: constants.MAP_PLYGN_SYTLE
    });
    this.polygonLayer.addTo(this.leafletMap);
    this.$store.state.polygons = this.polygons;
    // Focus map on most relevant AHJ 
    let initialPolygonSelected = this.polygons[0];
    this.$store.commit("setSelectedAHJIDFromTable", initialPolygonSelected.properties.AHJID);
    //this.selectPolygon(intialPolygonSelected);
   },
   // Focus the map on an AHJ and its polygon area
   selectPolygon(polygonAHJID, oldPolygonAHJID) { // TODO: pass polygon so that clicking on table adds mpoly to map (when address hasn't been searched)
      let map = this.leafletMap;
      map.eachLayer(function(layer) {
        if (layer.feature) {
          if (layer.feature.properties.AHJID === polygonAHJID) {
            map.fitBounds(layer.getBounds());
            layer.setStyle(constants.MAP_PLYGN_SLCTD_SYTLE());
          } else if (layer.feature.properties.AHJID === oldPolygonAHJID) {
            layer.setStyle(constants.MAP_PLYGN_SYTLE());
          }
        }
      });
    },
   // Add markers for each AHJ on the map
   updateMapMarkers(){
    if (this.currSearchMarker === null){
      var searchMarker = L.AwesomeMarkers.icon({
        icon: 'circle',
        prefix: 'fa',
        markerColor: 'cadetblue'
      });
      let marker = L.marker(this.$store.state.mapViewCenter, {icon: searchMarker}).addTo(this.leafletMap);
      this.currSearchMarker = marker;
      this.$store.commit("setLeafletMarker", marker);
    }
    for (let i = 0; i < this.polygons.length; i++){
      var ahjMarker = L.AwesomeMarkers.icon({
        icon: 'building',
        prefix: 'fa',
        markerColor: this.selectMarkerStyle(i, this.polygons[i].properties.ALAND)
        });
        // marker is currently hard coded to say there is no contact info for this AHJ
        let marker = L.marker([this.polygons[i].properties.INTPTLAT, this.polygons[i].properties.INTPTLON], {icon: ahjMarker, riseOnHover: true})
                        .bindTooltip("The Registry does not \n have Address or Contact Info \n for this AHJ.")
                        .addTo(this.markerLayerGroup);
        let that = this;
        marker.on('click', function(){
          that.$store.commit("setSelectedAHJIDFromTable", that.polygons[i].properties.AHJID);
          that.$store.commit("setCurrPolygon", i);
        })
      }
    },
    selectMarkerStyle(index, landArea){
      // REQUESTISFILTER IS ALWAYS FALSE WHICH WILL CAUSE PROBLEMS
      if (this.$store.state.requestIsFilter){
        if (landArea < 5_000_000_000)
          return 'lightblue'
        else if(landArea < 50_000_000_000)
          return 'blue'
        else  
          return 'darkblue'
      }
      else {
        return this.markerColors[index];
      }
    }
 },
 /*
  * Load the leaflet map when this component is mounted
  */
 mounted() {
   this.setupLeafletMap();
 },
 watch: {
   // Upon a new search, clear markers on map and add new polygons to map
   '$store.state.callData': function() {
    this.updateMap();
  },
  // Upon a row selected in the AHJ table, update map to focus on this AHJ
  /*'$store.state.currPolyInd': function() {
    this.selectPolygon(this.$store.state.polygons[this.$store.state.currPolyInd]);
  },*/
  "$store.state.selectedAHJID": function(newVal, oldVal) {
    console.log("watcher entered");
    console.log(`${newVal}, ${oldVal}`)
      this.selectPolygon(newVal, oldVal);
    },
  // The div containing the leaflet map changes during the first search, so we resize map. 
  '$store.state.showTable': function() {
    this.leafletMap.invalidateSize(true);
  },
 }
};
</script>

<style>
.ahj-public-list-container {
  display: grid;
  grid-template-columns: auto;
  height: 100%;
  padding-top: 5px;
  position: static;
}

#mapdiv {
  height: 100%;
  width: 100%;
  position: static;
}
</style>
