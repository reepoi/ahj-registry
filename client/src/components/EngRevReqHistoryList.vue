<template>
  <div class="ahj-public-list-container">
    <component-pagination class="pagination" id="top-buttons"></component-pagination>
    <div class="ahj-public-list">
      <b-table
        class="ahj-table"
        striped
        hover
        outlined
        small
        :fields="fields"
        :items="apiData.results"
        :busy="apiLoading"
      >
        <template v-slot:table-busy>
          <div class="text-center text-primary my-2">
            <b-spinner class="align-middle"></b-spinner>
            <strong>&nbsp; Loading...</strong>
          </div>
        </template>
      </b-table>
    </div>
    <component-pagination class="pagination" id="bottom-buttons"></component-pagination>
  </div>
</template>

<script>
import Pagination from "./Pagination.vue";
export default {
  props: ["admin_page"],
  data() {
    return {
      fields: [
        {
          key: "id",
          label: "Engineering Review Requirement ID",
          thStyle: { width: "274px" },
          class: "text-center",
          thClass: ".col-field-styling"
        },
        {
          key: "history_date",
          label: "Date",
          thStyle: { width: "274px" },
          class: "text-center",
          thClass: ".col-field-styling"
        },
        {
          key: "history_type",
          label: "Type",
          thStyle: { width: "274px" },
          class: "text-center",
          formatter: this.editTypeFormatter,
          thClass: ".col-field-styling"
        },
        // {
        //   key: "history_change_reason",
        //   label: "Comment",
        //   thStyle: { width: "274px" },
        //   class: "text-center",
        //   thClass: ".col-field-styling"
        // },
        {
          key: "history_user.email_address",
          label: "Changed By",
          thStyle: { width: "274px" },
          class: "text-center",
          thClass: ".col-field-styling"
        },
      ]
    };
  },
  beforeCreate() {
    this.$store.commit("setApiUrlAddon", "history/eng-rev-req/");
    this.$store.commit("setAPILoading", true);
    this.$store.commit("callHistoryAPI");
  },
  beforeDestroy() {
    this.$store.commit("deleteAPIData");
  },
  computed: {
    apiData() {
      return this.$store.state.apiData;
    },
    apiLoading() {
      return this.$store.state.apiLoading;
    },
    hasNext() {
      return this.$store.state.hasNext;
    },
    hasPrevious() {
      return this.$store.state.hasPrevious;
    },
    ahjCount() {
      return this.$store.state.ahjCount;
    },
    dataReady() {
      return this.$store.state.dataReady;
    }
  },
  methods: {
    editTypeFormatter(value) {
      switch(value) {
        case "+":
          return "Created";
        case "-":
          return "Deleted";
        case "~":
          return "Modified";
      }
    }
  },
  components: {
    "component-pagination": Pagination
  }
};
</script>

<style scoped>
.btn {
  margin: 5px;
}
.ahj-public-list-container {
  display: grid;
  grid-template-rows: 50px 720px 50px;
  grid-template-columns: auto;
  height: 100%;
  padding-top: 5px;
}

li {
  margin-top: -6px;
  margin-bottom: -6px;
}
ul {
  padding: 0;
  list-style: none;
}

.card {
  border: 2px solid #444549;
  box-shadow: 3px 3px 8px 0px rgba(0, 0, 0, 0.3);
  border-radius: 4px;
  height: 227px;
  width: 488px;
  padding: 10px;
  margin-right: 10px;
  margin-bottom: 10px;
  display: grid;
  grid-template-columns: 33% 1fr;
  grid-template-rows: 140px auto;
  font-family: "Roboto Condensed";
}

.logo {
  width: 140px;
  height: 140px;
  background-color: #d8d8d8;
}

.card-body {
  padding: 0;
  grid-column: 2 / 3;
}

.ahj-public-list {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  background-color: white;
  height: 725px;
  justify-content: flex-start;
  align-content: flex-start;
  grid-row: 2 / 3;
  grid-column: 1 /2;
  width: 1163px;
  overflow-y: auto;
}

a.nav-link {
  padding: 0px;
}

.loader {
  border: 16px solid #f3f3f3; /* Light grey */
  border-top: 16px solid #3498db; /* Blue */
  border-radius: 50%;
  width: 120px;
  height: 120px;
  animation: spin 2s linear infinite;
  margin-left: 400px;
  margin-top: 150px;
  grid-row: 2 / 3;
  grid-column: 1 /2;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

#top-buttons {
  grid-row: 1 / 2;
  margin-top: -20px;
  position: relative;
  margin-left: auto;
  margin-right: 0;
}

#bottom-buttons {
  grid-row: 3 / 4;
  position: relative;
  margin-left: auto;
  margin-right: 0;
}

.pagination {
  display: flex;
  justify-content: flex-end;
}

.btn-primary,
.btn-primary:hover,
.btn-primary:active,
.btn-primary:visited,
.btn-primary:focus,
.btn-primary:disabled {
  background-color: #1d4679;
  border-color: #1d4679;
}

a {
  color: #1d4679;
}

.ahj-table {
  margin-left: 0px;
}

.ahj-code-field-col {
  width: 400px;
  text-align: center;
}

.col-field-styling {
  text-align: center;
}

.table {
  margin-bottom: 0px !important;
}
</style>