<template>
  <div class="ahj-search-container">
    <!-- <div class="breadcrumbs">
      <router-link to="/" class="nav-link">Home Page</router-link>/
      <router-link to="/" class="nav-link disabled">Product Search</router-link>
    </div>-->
    <div class="download-search-results">
      <a href @click.prevent="exportResults">Download Search Results</a>
    </div>
    <div class="ahj-count">
      <br />
      <strong>{{ ahjCount }} AHJ Entry Changes</strong>
    </div>
    <div class="ahj-search-sidebar">
      <select v-model="listCatagory">
        <option value="ahj">AHJ</option>
        <option value="address">Address</option>
        <option value="location">Location</option>
        <option value="contact">Contact</option>
        <option value="eng-rev-req">Eng. Review Requirement</option>
      </select>
      <component-ahj-filter 
        :catagory="listCatagory"
      >
      </component-ahj-filter>
    </div>
    <div class="ahj-search-body">
      <component
        :is="dynamicList"
      >
      </component>
    </div>
  </div>
</template>

<script>
import AHJHistoryFilter from "../components/AHJHistoryFilter.vue";
import AHJHistoryList from "../components/AHJHistoryList.vue";
import AddressHistoryList from "../components/AddressHistoryList.vue";
import ContactHistoryList from "../components/ContactHistoryList.vue";
import LocationHistoryList from "../components/LocationHistoryList.vue";
import EngRevReqHistoryList from "../components/EngRevReqHistoryList.vue";
export default {
  props: ["admin_page"],
  data() {
    return {
      listCatagory: "ahj"
    }
  },
  components: {
    "component-ahj-filter": AHJHistoryFilter
  },
  created() {
    this.$store.commit("deleteAPIData");
  },
  computed: {
    dynamicList() {
      switch(this.listCatagory) {
        case "ahj":
          return AHJHistoryList;
        case "address":
          return AddressHistoryList;
        case "contact":
          return ContactHistoryList;
        case "location":
          return LocationHistoryList;
        case "eng-rev-req":
          return EngRevReqHistoryList;
      }
    },
    ahjCount() {
      return this.$store.state.ahjCount;
    }
  },
  methods: {
    exportResults() {
      this.$store.commit("exportResults");
    }
  }
};
</script>

<style scoped>
.ahj-search-container {
  margin-top: 20px;
  display: grid;
  grid-template-columns: 0px 250px 15px auto 25px;
  grid-template-rows: 25px auto;
}

.ahj-search-sidebar {
  grid-column: 2 / 3;
  grid-row: 1 / 3;
}

.ahj-search-body {
  grid-column: 4 / span 2;
  grid-row: 1 / span 2;
}

.breadcrumbs {
  grid-column: 2 / span 3;
  grid-row: 1 / 2;
}

.nav-link {
  display: inline;
  padding: 0;
  padding-right: 5px;
}

.download-search-results {
  grid-column: 4 / 5;
  grid-row: 1 / 2;
  font-family: "Roboto Condensed";
}

#sort-by-button {
  float: right;
}

.ahj-count {
  grid-column: 4 / 5;
  grid-row: 1 / 2;
  font-family: "Roboto Condensed";
}

a {
  color: #4285f4;
}
</style>
