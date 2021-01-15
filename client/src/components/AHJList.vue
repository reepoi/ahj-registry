<template>
 <div class="ahj-table-info-container">
  
   <b-table ref="selectableTable" class="ahj-table" id="ahj-table" selected-variant='' selectable :select-mode="'single'" @row-selected="onRowSelected" outlined small :fields="fields" :items="callData" :busy="apiLoading">
       <template v-slot:table-busy>
         <div class="text-center text-primary my-2">
           <b-spinner class="align-middle"></b-spinner>
           <strong>&nbsp; Loading...</strong>
         </div>
       </template>
       <template #cell(more_info)="row">
         <b-button size="sm" @click="row.toggleDetails" class="mr-2">
           {{ row.detailsShowing ? 'Hide' : 'Show'}}
         </b-button>
       </template>
 
     <template #row-details="row">
       <b-card>

         <b-row class="mb-2">
           <b-col sm="3" class="text-sm-right"><b>Address:</b></b-col>
           <b-col sm="5">{{(typeof(row.item.FireCode.Value) !== "") ? 'No address information available for this AHJ.' : row.item.FireCode.Value}}</b-col>
         </b-row>
 
         <b-row class="mb-2">
           <b-col sm="3" class="text-sm-right"><b>Contact:</b></b-col>
           <b-col sm="5">{{(typeof(row.item.FireCode.Value) !== "") ? 'No contact information available for this AHJ.' : row.item.FireCode.Value}}</b-col>
         </b-row>

         <b-row class="mb-2">
           <b-col sm="3" class="text-sm-right"><b>Additional Building Code Info:</b></b-col>
           <b-col cols="2">{{'None.'}}</b-col>
         </b-row>

         <b-row class="mb-2">
           <b-col sm="9" class="text-sm-right"><b>To edit AHJ information or learn about submitting an application, visit this AHJ's profile:</b></b-col>
           <b-button size="sm" @click="row.toggleDetails">AHJ Profile</b-button>
         </b-row>

       </b-card>
     </template>
 
   </b-table>
 </div>
</template>

 
<script>
export default {
  name: "Table",
 data() {
   return{
     table: null,
     tableEntries: null,
     fields: [
        {
          label: "Show Details",
          thStyle: { width: "274px" },
          class: "text-center",
          thClass: ".col-field-styling"
        },
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
          key: "BuildingCode.Value",
          label: "Building Code",
          thStyle: { width: "274px" },
          class: "text-center",
          thClass: ".col-field-styling"
        },
        {
          key: "ElectricCode.Value",
          label: "Electric Code",
          thStyle: { width: "274px" },
          class: "text-center",
          thClass: ".col-field-styling"
        },
        {
          key: "FireCode.Value",
          label: "Fire Code",
          thStyle: { width: "274px" },
          class: "text-center",
          thClass: ".col-field-styling"
        },
        {
          key: "ResidentialCode.Value",
          label: "Residential Code",
          thStyle: { width: "274px" },
          class: "text-center",
          thClass: ".col-field-styling"
        },
        "more_info"
      ],
      selectedAHJ: {}
   }

 },
 computed: {
   callData(){
     return this.$store.state.callData;
   },
   apiLoading(){
     return this.$store.state.apiLoading;
   }
  },
methods: {
  selectRow(index){
    this.clearSelectedRow();
    let row = document.getElementById("ahj-table").rows[index+1];
    row.classList.add("b-table-row-selected");
  },
    onRowSelected(items) {
      this.clearSelectedRow();
      for (let i = 0; i < this.$refs.selectableTable.selectedRows.length; i++) {
        if (this.$refs.selectableTable.selectedRows[i]) {
          this.$store.commit('setCurrPolygon', i);
          this.$store.commit("setSelectedAHJIDFromTable", items[0].AHJID.Value);
          return;
        }
      }  
    },
  clearSelectedRow() {
    let selected = document.getElementsByClassName("b-table-row-selected");
    if (selected.length !== 0){
      selected[0].classList.remove("b-table-row-selected");
    }
 },
},
watch: {
   '$store.state.callData': function() {
  },
  '$store.state.currPolyInd': function() {
    this.selectRow(this.$store.state.currPolyInd);
  }
 }
};
</script>

<style>
  h2 {
    text-align: center;
    padding-bottom: 0.5em;
  }
  table {
    border: 1px solid black;
    margin: 0 auto;
  }
  td {
    text-align: center;
    padding: 15px;
    min-width:120px;
    max-width:120px;
    font-size: 1.2em;
  }
  .b-table-row-selected {
    border: 3px solid #85e9f2;
  }
  .ahj-table tbody tr:hover td{
    background-color: #e3fcf9;
  }
  .ahj-table tbody tr:nth-child(odd){
    background-color: #fff2e5;
  }
  tr:nth-child(even) {
    background-color: #ffffff;
  }
</style>
