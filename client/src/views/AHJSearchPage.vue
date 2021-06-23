<template>
  <div class="ahj-search-container">
    <div class="ahj-search-filter">
      <ahj-search-filter></ahj-search-filter>
    </div>
    <div class="ahj-search-map">
      <component-mapview></component-mapview>
    </div>
    <div class="ahj-table-sidebar" v-show="$store.state.showTable">
      <div class="table-info">
        <component-ahj-table-result-info class="ahj-table-result-info"></component-ahj-table-result-info>
        <component-ahj-table-pagination class="ahj-table-pagination"></component-ahj-table-pagination>
      </div>
      <component-ahj-table-view></component-ahj-table-view>
    </div>
  </div>
</template>

<script>
import MapView from "../components/MapView.vue";
import AHJTableView from "../components/AHJTableView.vue";
import AHJSearchPageFilter from "../components/AHJSearchPageFilter.vue";
import AHJTablePagination from "../components/AHJTablePagination";
import AHJTableResultInfo from "../components/AHJTableResultInfo";
export default {
  created() { // called before 'mounted' is called for child components
    this.$store.commit("setShowTable", false);
  },
  components: {
    "ahj-search-filter": AHJSearchPageFilter,
    "component-mapview": MapView,
    "component-ahj-table-result-info": AHJTableResultInfo,
    "component-ahj-table-pagination": AHJTablePagination,
    "component-ahj-table-view": AHJTableView
  }
};
</script>

<style scoped>
.ahj-search-container {
  display: grid;
  grid-template-columns: auto fit-content(40%);
}

.ahj-search-filter {
  grid-column: 1;
  grid-row: 1 / 3;
}

.ahj-search-map {
  grid-column: 1;
  grid-row: 1 / 3;
}

.ahj-table-sidebar {
  grid-column: 2;
  grid-row: 1 / span 2;
  padding-left: 1em;
}

.table-info {
  display: grid;
  background: white;
}

.ahj-table-result-info {
  grid-column: 1;
}

.ahj-table-pagination {
  grid-column: 2;
  text-align: right;
}
@media (max-width: 1000px){
.ahj-search-container {
  grid-template-rows: auto fit-content(40%);
}

.ahj-search-filter {
  grid-row: 1 / 2;
}

.ahj-search-map {
  grid-row: 1 / 2;
}

.ahj-table-sidebar {
  grid-column: 1;
  grid-row: 2 / 3;
}
}
</style>
