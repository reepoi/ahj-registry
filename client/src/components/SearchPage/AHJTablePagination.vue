<template>
  <div class="page-select">
    <b-button-group>
      <b-button variant="outline-secondary" @click="callForPage(1)"><b-icon icon="chevron-double-left" font-scale="1"></b-icon></b-button>
      <b-button variant="outline-secondary" @click="callForPage(currentPage - 1)"><b-icon icon="chevron-left" font-scale="1"></b-icon></b-button>
      <b-form-input list="pagination-list" @change="callForPage(userInputPage)" v-model="userInputPage" :options="pages" :state="pageNumValidation(Number(userInputPage))"></b-form-input>
      <b-form-datalist id="pagination-list" @change="callForPage(userInputPage)" :options="pages"></b-form-datalist>
      <b-button variant="outline-secondary" @click="callForPage(currentPage + 1)"><b-icon icon="chevron-right" font-scale="1"></b-icon></b-button>
      <b-button variant="outline-secondary" @click="callForPage(pages[pages.length - 1])"><b-icon icon="chevron-double-right" font-scale="1"></b-icon></b-button>
    </b-button-group>
  </div>
</template>

<script>

export default {
  data() {
    return {
      perPage: 20, // value from django rest framework pagination
      userInputPage: '1',
      currentPage: 1,
      pages: []
    };
  },
  methods: {
    /**
     * set the page of the AHJ table
     * @param count number of ahjs that match search query
     */
    setPagination(count) {
      let numPages = Math.floor(count / this.perPage) + 1;
      for (let i = 1; i <= numPages; i++) {
        this.pages.push(i);
      }
    },
    /**
     * Reset pagination state when new search is made
     */
    resetPagination() {
      this.pages = [];
      this.currentPage = 1;
      this.userInputPage = '1';
    },
    /**
     * Searches the currently made search with the proper page offset
     * @param pageNum the page number requested by the user
     */
    callForPage(pageNum) {
      // check new page is a valid page number and not the current page
      pageNum = Number(pageNum);
      if (this.currentPage === pageNum || this.pageNumValidation(pageNum) === false) { // null is used for 'ok' input in validation so must check explicitly is false
        return;
      }

      // add the pagination to the current query
      let currentQuery = this.$store.state.searchedQuery;
      let limit = this.perPage;
      let offset = (pageNum - 1) * limit;
      let paginationLimitOffset = `limit=${limit}&offset=${offset}&`;
      this.currentPage = pageNum;
      this.userInputPage = pageNum;
      currentQuery['Pagination'] = paginationLimitOffset;
      this.$store.commit("callAPI", currentQuery);
    },
    pageNumValidation(pageNum) {
      if (pageNum === 1 || (pageNum >= 1 && pageNum <= this.pages[this.pages.length - 1])) {
        return null; // return null instead of true to remove green checkmark
      }
      return false;
    }
  },
  watch: {
    /**
     * Listener to determine if a new serach was made
     * @param newValue the new selected ahj, may be null
     * @param oldValue the old selected ahj, may be null
     */
    '$store.state.selectedAHJ': function (newValue, oldValue) {
      if (newValue === null) { // new search was made
        this.resetPagination();
      } else if (oldValue === null) { // new search is complete
        let ahjCount = this.$store.state.apiData['count'];
        this.setPagination(ahjCount);
      }
    }
  }
};
</script>

<style scoped>

.page-select {
  margin: 0.5rem;
}

::v-deep input.form-control {
  border-radius: 0;
  border-color: #6c757d;
  outline: 0;
  width: 5em;
}

</style>
