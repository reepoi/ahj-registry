<template>
  <div class="page-select">
    <b-button-group>
      <b-button variant="outline-secondary" @click="callForPage(1)"><b-icon icon="chevron-double-left" font-scale="1"></b-icon></b-button>
      <b-button variant="outline-secondary" @click="callForPage(currentPage - 1)"><b-icon icon="chevron-left" font-scale="1"></b-icon></b-button>
      <b-form-input list="pagination-list" @change="callForPage(currentPage)" v-model="currentPage" :options="pages" :state="pageNumValidation"></b-form-input>
      <b-form-datalist id="pagination-list" @change="callForPage(currentPage)" :options="pages"></b-form-datalist>
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
      currentPage: '',
      pages: []
    };
  },
  methods: {
    setPagination(count) {
      let numPages = Math.floor(count / this.perPage) + 1;
      for (let i = 1; i <= numPages; i++) {
        this.pages.push(i);
      }
    },
    resetPagination() {
      this.pages = [];
      this.currentPage = '';
    },
    callForPage(pageNum) {
      if (this.currentPage === '' || this.pageNumValidation === false) { // null is used for 'ok' input in validation so must check explicitly is false
        return;
      }
      let currentQuery = this.$store.state.searchedQuery;
      let limit = this.perPage;
      let offset = (pageNum - 1) * limit;
      let paginationLimitOffset = `limit=${limit}&offset=${offset}&`;
      this.currentPage = pageNum;
      currentQuery['Pagination'] = paginationLimitOffset;
      this.$store.commit("callAPI", currentQuery);
    }
  },
  computed: {
    pageNumValidation() {
      if (this.currentPage === '' || (this.currentPage >= 1 && this.currentPage <= this.pages[this.pages.length - 1])) {
        return null; // return null instead of true to remove green checkmark
      }
      return false;
    }
  },
  watch: {
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
