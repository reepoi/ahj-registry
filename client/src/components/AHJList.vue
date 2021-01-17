<template>
  <div class="ahj-public-list-container">
    <component-pagination class="pagination" id="top-buttons"></component-pagination>
    <div class="ahj-public-list">
      <b-table
        ref="selectableTable"
        class="ahj-table"
        selectable
        :select-mode="'single'"
        selected-variant=""
        @row-clicked="onRowClicked"
        hover
        outlined
        small
        :fields="fields"
        :items="apiData.results ? apiData.results.ahjlist : undefined"
        :busy="apiLoading"
      >
        <template #table-busy>
          <div class="text-center text-primary my-2">
            <b-spinner class="align-middle"></b-spinner>
            <strong>&nbsp; Loading...</strong>
          </div>
        </template>
        <template v-slot:cell(more_info)="row">
          <b-button size="sm" @click="row.toggleDetails" class="mr-2">
            {{ row.detailsShowing ? "Hide" : "Show" }}
          </b-button>
        </template>
        <template #row-details="row">
          <b-card>
            <component-edit-page ref="editpage" :mode="editPageMode" :selectedAHJ="row.item"></component-edit-page>
          </b-card>
        </template>
      </b-table>
    </div>
    <component-pagination class="pagination" id="bottom-buttons"></component-pagination>
  </div>
</template>

<script>
import Pagination from "./Pagination.vue";
import EditPage from "./EditPage.vue";
export default {
  components: {
    "component-pagination": Pagination,
    "component-edit-page": EditPage
  },
  props: ["admin_page"],
  data() {
    return {
      fields: [
        {
          key: "AHJCode.Value",
          label: "AHJ Code",
          thStyle: { width: "274px" },
          class: "text-center",
          thClass: ".col-field-styling"
        },
        {
          key: "AHJName.Value",
          label: "AHJ Name",
          thStyle: { width: "274px" },
          class: "text-center",
          thClass: ".col-field-styling"
        },
        {
          key: "Address.County.Value",
          label: "County",
          thStyle: { width: "274px" },
          class: "text-center",
          thClass: ".col-field-styling"
        },
        {
          key: "BuildingCode.Value",
          label: "Building Code",
          thStyle: { width: "274px" },
          class: "text-center",
          formatter: this.ahjCodeFormatter,
          thClass: ".col-field-styling"
        },
        {
          key: "ElectricCode.Value",
          label: "Electric Code",
          thStyle: { width: "274px" },
          class: "text-center",
          formatter: this.ahjCodeFormatter,
          thClass: ".col-field-styling"
        },
        {
          key: "FireCode.Value",
          label: "Fire Code",
          thStyle: { width: "274px" },
          class: "text-center",
          formatter: this.ahjCodeFormatter,
          thClass: ".col-field-styling"
        },
        {
          key: "ResidentialCode.Value",
          label: "Residential Code",
          thStyle: { width: "274px" },
          class: "text-center",
          formatter: this.ahjCodeFormatter,
          thClass: ".col-field-styling"
        },
        {
          key: "WindCode.Value",
          label: "Wind Code",
          thStyle: { width: "274px" },
          class: "text-center",
          formatter: this.ahjCodeFormatter,
          thClass: ".col-field-styling"
        },
        "more_info"
      ],
      editPageMode: "update",
      editPageViewOnly: true
    };
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
    onRowClicked(rowItem) {
      this.$store.commit("setSelectedAHJ", rowItem);
    },
    ahjCodeFormatter(value) {
      if(value) {
        if (value === "NoSolarRegulations") {
          return "No Solar Regulations";
        }
        return value.substring(0, 4) + " " + value.substring(4);
      }
      return value;
    },
    nextPage() {
      this.$store.commit("toggleAPILoading");
      return this.$store.commit("callAPI", this.$store.state.nextPage);
    },
    previousPage() {
      this.$store.commit("toggleAPILoading");

      return this.$store.commit("callAPI", this.$store.state.previousPage);
    },
    selectRow(ahj) {
      if (!this.$store.state.apiLoading) {
        let ahjlist = this.$store.state.apiData.results.ahjlist;
        for (let i = 0; i < ahjlist.length; i++) {
          if (ahjlist[i].AHJID.Value === ahj.AHJID.Value) {
            this.$refs.selectableTable.selectRow(i);
          }
        }
      }
    }
  },
  watch: {
    "$store.state.selectedAHJ": function(newVal) {
      if (newVal !== null) {
        this.selectRow(newVal);
      }
    }
  }
};
</script>

<style scoped>
.ahj-public-list-container {
  height: 100%;
}

.ahj-public-list {
  height: 78vh;
  overflow-y: scroll;
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

a {
  color: #1d4679;
}

.ahj-table {
  margin-left: 0px;
}

::v-deep .table > tbody > tr.b-table-row-selected {
  border: 3px solid #85e9f2;
}

::v-deep .table.b-table.table-hover > tbody > tr:hover td {
  background-color: #e3fcf9;
}

::v-deep .table > tbody > tr:nth-child(odd){
  background-color: #fff2e5;
}

::v-deep .table > tbody > tr:nth-child(even) {
  background-color: #ffffff;
}
</style>
