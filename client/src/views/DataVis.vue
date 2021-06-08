<template>
  <div class="ahj-search-container">
    <div class="map-sidebar">
      <div class="map-sub-title">
        <h1>Permit Information Coverage</h1>
        <h1>of the United States</h1>
      </div>
      <div class="map-body">
        <h4>Explore where the AHJ Registry has permitting information across these categories:</h4>
        <div class="map-body-list">
          <div class="map-body-list-item" v-for="category in mapCategories" :key="category.value">
            <input type="radio" :id="'map-radio-' + category.value" :value="category.value" v-model="mapCategory"/>
            <label :for="'map-radio-' + category.value">{{ category.text }}</label>
          </div>
        </div>
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
      mapCategories: [ // categories for different statistics for the data completion map
        { value: 'all', text: 'All Categories' },
        { value: 'numBuildingCodes', text: 'Building Codes' },
        { value: 'numElectricCodes', text: 'Electric Codes' },
        { value: 'numResidentialCodes', text: 'Residential Codes' },
        { value: 'numFireCodes', text: 'Fire Codes' },
        { value: 'numWindCodes', text: 'Wind Codes' }
      ]
    }
  },
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
  padding-bottom: 4em;
  text-align: center;
  grid-area: map-sub-title;
}

.data-vis-map {
  grid-area: map;
}

.map-body {
  padding-right: 5em;
  padding-left: 5em;
  grid-area: map-body;
}

.map-body-list{
  display: flex;
  flex-direction: column;
}

.map-body-list-item {
  padding-left: 2em;
  font-size: 1.2em;
  min-width: 10em;
}

.map-body-list-item > input {
  margin-right: 0.5em;
}

@media (max-width: 1000px){
  h1 {
    font-size: 1.8rem;
  }
  h4 {
    font-size: 1.3rem;
  }
  .map-body-list{
    display: grid;
    grid-template-columns: 33% 33% 33%;
    grid-template-rows: auto auto;
  }
  .ahj-search-container {
    grid-template-columns: 100%;
    grid-template-rows: 10% minmax(25%, auto) 60vh;
    grid-template-areas:
      "map-sub-title"
      "map-body"
      "map"
  }
  .map-body-list-item {
    padding: 0;
  }
  .map-body-list {
    flex-direction: row;
  }
  .map-sub-title {
    padding-bottom: 1em;
  }
  .map-body {
    width: 85%;
    margin: 0 auto 1em;
  }
}

@media (max-width: 800px){
  .ahj-search-container {
    grid-template-rows: 10% minmax(25%, auto) 60vh;
  }
  .map-body-list{
    grid-template-columns: 50% 50%;
    grid-template-rows: auto auto auto;
  }

  .map-body {
    width: 90%;
    padding-right: 2%;
    padding-left: 2%;
  }
}

</style>
