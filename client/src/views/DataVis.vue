<template>
  <div class="ahj-search-container">
   <div class="map-sub-title">
      <h1>Permit Information Coverage</h1>
      <h1>of the United States</h1>
    </div>
    <div class="map-body">
      <h4>Explore where the AHJ Registry has permitting information across these categories:</h4>
      <div class="map-body-list" v-for="category in mapCategories" :key="category.value">
        <input type="radio" :id="'map-radio-' + category.value" :value="category.value" v-model="mapCategory"/>
        <label :for="'map-radio-' + category.value">{{ category.text }}</label>
        <br/>
      </div>
    </div>
    <component-data-vis-map class="data-vis-map" :selected-map-category="mapCategory" :map-categories="mapCategories.map(cat => cat.value)"/>
  </div>

</template>

<script>
import DataVisMap from "../components/DataVisMap.vue";
export default {
  components: {
    'component-data-vis-map': DataVisMap,
  },
  data() {
    return {
      mapCategory: 'all',
      mapCategories: [
        { value: 'all', text: 'All Categories' },
        { value: 'numBuildingCodes', text: 'Building Codes' },
        { value: 'numElectricCodes', text: 'Electric Codes' },
        { value: 'numResidentialCodes', text: 'Residential Codes' },
        { value: 'numFireCodes', text: 'Fire Codes' },
        { value: 'numWindCodes', text: 'Wind Codes' }
      ]
    }
  }
};
</script>

<style scoped>
.ahj-search-container {
  display: grid;
  grid-template-columns: 60% 40%;
  grid-template-rows: 12em auto;
  grid-template-areas:
      "map map-sub-title"
      "map map-body"
}

.map-sub-title {
  padding-top: 2em;
  text-align: center;
  grid-area: map-sub-title;
}

.data-vis-map {
  grid-area: map;
}

.map-body {
  text-align: justify;
  padding-right: 5em;
  padding-left: 5em;
  grid-area: map-body;
}

.map-body-list {
  padding-left: 2em;
  font-size: 1.2em;
}

.map-body-list > input {
  margin-right: 0.5em;
}

</style>
