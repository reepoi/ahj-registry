<template>
  <div class="public-filter">
    <form @submit.prevent>
      <div class="form-group">
        <h1>Search by Address or Coordinates</h1>
        <input id="address" type="text" class="form-control search-input" v-model="query_data.Address"
               placeholder="Address or Coordinates"/>
      </div>
      <div id='drop' class="form-group dropdown-content">
        <div class='bcshow' @click='showapisettings'>
          <i id='plusbuttonAPI' class="fas fa-plus"></i>
          API Settings
        </div>
        <div id='apisettings' class='dropdown-content'>
          <h2>View Edits As</h2>
          <b-form-select v-model="query_data.view" :options="choiceFields.APIEditViewMode" />
        </div>
        <div class='bcshow' @click='showbc'>
          <i id='plusbutton' class="fas fa-plus"></i>
          Building Codes
        </div>
        <div id='bcdrop' class='dropdown-content'>
          <h2>Building Codes</h2>
          <b-form-select v-model="query_data.BuildingCode" :options="choiceFields.AHJ.BuildingCode" multiple
                         :select-size="2"/>
          <h2>Electric Codes</h2>
          <b-form-select v-model="query_data.ElectricCode" :options="choiceFields.AHJ.ElectricCode" multiple
                         :select-size="2"/>
          <h2>Fire Codes</h2>
          <b-form-select v-model="query_data.FireCode" :options="choiceFields.AHJ.FireCode" multiple :select-size="2"/>
          <h2>Residential Codes</h2>
          <b-form-select v-model="query_data.ResidentialCode" :options="choiceFields.AHJ.ResidentialCode" multiple
                         :select-size="2"/>
          <h2>Wind Codes</h2>
          <b-form-select v-model="query_data.WindCode" :options="choiceFields.AHJ.WindCode" multiple :select-size="2"/>
        </div>
        <div class='ahjshow' @click='showahj'>
          <i id='plusbuttonAHJ' class="fas fa-plus"></i>
          More Search Options
        </div>
        <div id="ahjdrop" class='dropdown-content'>
          <input id="ahjname" type="text" class="form-control search-input" v-model="query_data.AHJName"
                 placeholder="AHJ Name"/>
          <input id="ahjcode" type="text" class="form-control search-input" v-model="query_data.AHJCode"
                 placeholder="AHJ Code"/>
          <b-form-select v-model="query_data.AHJLevelCode" :options="choiceFields.AHJ.AHJLevelCode" />
          <input id="stateprovince" type="text" class="form-control search-input" v-model="query_data.StateProvince"
                 placeholder="State/Province"/>
          <input id="ahjid" type="text" class="form-control search-input" v-model="query_data.AHJID"
                 placeholder="AHJ ID"/>
        </div>
      </div>
      <div class="button-group">
        <button type="button" class="btn btn-primary" @click="clearFilters">Clear</button>
        <button type="button" class="btn btn-primary" @click="updateQuery">Search
        </button>
      </div>
      <div id='showbutton' class="drop" @click='show'>
        <i width=12 class="arrow fas fa-chevron-down"></i>
      </div>
      <div id='hidebutton' class='drop dropdown-hide' @click='show'>
        <i width=12 class="arrow fas fa-chevron-up"></i>
      </div>
    </form>
  </div>
</template>

<script>
import constants from "../constants.js";
export default {
  data() {
    return {
      query_data: {
        view: "latest",
        AHJName: "",
        AHJCode: "",
        AHJLevelCode: "",
        AHJID: "",
        Address: "", // Location (latlng) searches are done through the Address field
        BuildingCode: [],
        ElectricCode: [],
        FireCode: [],
        ResidentialCode: [],
        WindCode: [],
        StateProvince: ""
      },
      choiceFields: constants.CHOICE_FIELDS
    };
  },
  methods: {
    updateQuery() {
      let queryString = "";
      Object.keys(this.query_data).forEach(key => {
        if(this.query_data[key] !== ""){
          if(Array.isArray(this.query_data[key])){
            if(this.query_data[key].length > 0 && this.query_data[key][0] !== ""){
              queryString += key + "=";
              for(let i = 0; i < this.query_data[key].length; i++){
                queryString += this.query_data[key][i];
                if(i !== this.query_data[key].length - 1){
                  queryString += ", ";
                }
              }
              queryString += "&";
            }
          } else {
            queryString += key + "=" + this.query_data[key] + "&";
          }
        }
      });
      this.$store.commit("setQueryString", queryString);
      this.$store.commit("setAPILoading", true);
      this.$store.commit("setSelectedAHJ", null);
      this.$store.commit("deleteAPIData");
      this.$store.commit("callAPI", queryString);
    },
    clearFilters() {
      this.searchKeyword = "";
      this.query_data = {
        view: "latest",
        AHJName: "",
        AHJCode: "",
        AHJLevelCode: "",
        AHJID: "",
        Address: "", // Location (latlng) searches are done through the Address field
        BuildingCode: [],
        ElectricCode: [],
        FireCode: [],
        ResidentialCode: [],
        WindCode: [],
        StateProvince: ""
      };
      this.$store.commit("setQueryString", "");
      this.$store.commit("updateCurrentPage", 1);
    },
    show(){
      document.getElementById('drop').classList.toggle('show')
      document.getElementById('showbutton').classList.toggle('dropdown-hide')
      document.getElementById('hidebutton').classList.toggle('dropdown-hide')
    },
    showbc(){
      document.getElementById('bcdrop').classList.toggle('show')
      var plus = document.getElementById('plusbutton')
      plus.classList.toggle('fa-plus');
      plus.classList.toggle('fa-minus')
    },
    showahj(){
      document.getElementById('ahjdrop').classList.toggle('show')
      var plus = document.getElementById('plusbuttonAHJ')
      plus.classList.toggle('fa-plus');
      plus.classList.toggle('fa-minus')
    },
    showapisettings() {
      document.getElementById('apisettings').classList.toggle('show')
      var plus = document.getElementById('plusbuttonAPI')
      plus.classList.toggle('fa-plus');
      plus.classList.toggle('fa-minus');
    }
  }
};
</script>

<style scoped>
h1 {
  font-size: 18px;
  color: #4b4e52;
  font-weight: bold;
  z-index: 500;
  display: block;
  margin: 0 auto;
  text-align: center;
}
h2 {
  font-size: 14px;
  font-weight: bold;
  text-align: center;
}
select {
  display: block;
  margin: 0 auto;
}
.public-filter {
  position: relative;
  padding-top: 5px;
  top: 10%;
  z-index: 500;
  width: 175px;
  background: rgba(255,255,255, 0.8);
  border: 1px solid black;
  border-radius: 8px;
  font-family: "Open Sans";
}
.form-group {
  display: block;
}
button {
  margin: 0px;
  margin-bottom: 15px;
  margin-right: 10px
}
label {
  display: block;
}
.button-group {
  display: flex;
  justify-content: flex-end;
  z-index: 500;
}
.btn-primary,
.btn-primary:active,
.btn-primary:visited,
.btn-primary:focus,
.btn-primary:disabled {
  background-color: white;
  border-color: #4b4e52;
  color: #4b4e52;
  border-radius: 20px;
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
.search-input {
  width: 95%;
  display: block;
  margin: 0 auto;
  border-radius: 20px;
  margin-bottom: 0px;
}
.dropdown-content{
  display: none;
}
.show {
  display: block;
}
.dropdown-hide {
  display: none;
}
.arrow{
  display: block;
  width: 12px;
  margin: auto;
}
.bcdrop-content{
  display: none;
}
</style>
