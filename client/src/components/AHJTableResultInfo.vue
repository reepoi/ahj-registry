<template>
  <div class="table-info">
    <b-dropdown text="Download Results" class="m-md-2" :disabled="ahjCount === 0">
      <template #button-content>
        <span v-if="resultsDownloading">
          Downloading... (<b-spinner small class="text-center" />
          {{ downloadCompletionPercent }}%)
        </span>
        <span v-else-if="!performedSearch">
          Loading...
        </span>
        <span v-else>
          Download {{ ahjCount }} Results
        </span>
      </template>
      <b-dropdown-item :disabled="resultsDownloading" @click="exportSearchResultsJSONCSV('application/json')">JSON (.json)</b-dropdown-item>
      <b-dropdown-item :disabled="resultsDownloading" @click="exportSearchResultsJSONCSV('text/csv')">CSV (.csv)</b-dropdown-item>
    </b-dropdown>
  </div>
</template>

<script>

export default {
  data() {
    return {
      ahjCount: 0,
      performedSearch: false
    };
  },
  methods: {
    exportSearchResultsJSONCSV(fileType) {
      this.$store.commit("exportSearchResultsJSONCSV", fileType);
    }
  },
  computed: {
    apiLoading() {
      return this.$store.state.apiLoading;
    },
    resultsDownloading() {
      return this.$store.state.resultsDownloading;
    },
    downloadCompletionPercent() {
      return this.$store.state.downloadCompletionPercent;
    }
  },
  watch: {
    '$store.state.apiLoading': function(newValue) {
      if (newValue) { // new search was made
        this.ahjCount = 0;
        this.performedSearch = false;
      } else { // new search is complete
        this.ahjCount = this.$store.state.apiData['count'];
        this.performedSearch = true;
      }
    }
  }
};
</script>

<style scoped>
.table-info {
  display: inline;
}
</style>
