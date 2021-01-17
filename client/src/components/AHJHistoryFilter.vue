<template>
  <div class="public-filter">
    <form @submit.prevent>
      <h1>Keyword</h1>
      <div class="form-group">
        <input
          type="text"
          class="form-control"
          id="keyword_search"
          v-model="searchKeyword"
          :placeholder="catagoryText"
          @keyup.enter="updateQuery"
        />
      </div>
      <div class="button-group">
        <button type="button" class="btn btn-primary" @click="updateQuery">
          <v-icon name="search" class="search-icon" />&nbsp; Search
        </button>
        <button type="button" class="btn btn-primary" @click="clearFilters">
          <v-icon name="times" class="clear-icon" />&nbsp;&nbsp;Clear filters
        </button>
      </div>
    </form>
  </div>
</template>

<script>
export default {
  props: ['catagory'],
  data() {
    return {
      searchKeyword: ""
    };
  },
  computed: {
    catagoryText() {
      switch(this.catagory) {
        case "ahj":
          return "AHJID or AHJName...";
        case "address":
          return "AHJID or ContactID...";
        case "contact":
          return "Name, AHJID or ContactID...";
        case "location":
          return "AddressID...";
        case "eng-rev-req":
          return "AHJID..."
      }
    }
  },
  methods: {
    updateQuery() {
      let searchString = "search=";
      if (this.searchKeyword) {
        // Split keywords
        let queryStrings = this.searchKeyword.split(" ");
        for(let i = 0; i < queryStrings.length - 1; i++) {
          searchString += queryStrings[i] + ",";
        }
        searchString += queryStrings[queryStrings.length - 1] + "&";
      } else {
        // Don't search if no keywords were provided
        return;
      }
      this.$store.commit("setQueryString", searchString);
      this.$store.commit("setAPILoading", true);
      this.$store.commit("deleteAPIData");
      this.$store.commit("callHistoryAPI", searchString);
    },
    clearFilters() {
      // Don't clear if there is no query to clear
      if(this.$store.state.queryString === "") {
        return;
      }
      this.searchKeyword = "";
      this.$store.commit("setQueryString", "");
    }
  }
};
</script>

<style scoped>
.clear-icon {
  color: #db4437;
  margin-bottom: 3px;
}

.search-icon {
  color: #4285f4;
  margin-bottom: 3px;
}
h1 {
  font-size: 18px;
  color: #4b4e52;
  font-family: "Roboto Condensed";
  font-weight: bold;
}

.public-filter {
  padding-left: 20px;
  padding-top: 5px;
}

.form-group {
  font-family: "Roboto Condensed";

  display: block;
}

button {
  margin: 5px;
  margin-bottom: 15px;
}

label {
  display: block;
}

.button-group {
  display: flex;
  justify-content: center;
  margin-bottom: 5px;
  margin-left: -17px;
}

.btn-primary,
.btn-primary:active,
.btn-primary:visited,
.btn-primary:focus,
.btn-primary:disabled {
  background-color: white;
  border-color: #4b4e52;
  color: #4b4e52;
}

.btn-primary:hover {
  background-color: #eeeeee;
  color: #4b4e52;
  border-color: #4b4e52;
}

label {
  margin-top: 3px;
  margin-bottom: 3px;
}

#keyword_search {
  width: 214px;
}
</style>
