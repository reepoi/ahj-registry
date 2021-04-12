<template>
  <div class="leaderboard-component-container">
    <h1>
      AHJ Registry Rankings
    </h1>
    <h5>
      Filter leaderboard by:
    </h5>
    <div class="leaderboard-input">
      <b-form-select text-field="name" value-field="item" v-model="SearchOption" :options="['CommunityScore', 'NumAcceptedEdits']" class="form-select"/>
      <input id="stateName" type="text" class="form-control search-input" v-model="StateProvince"
                 placeholder="State"/>
     <!--  <b-form-select v-model="Country" :options="['USA']" class="form-select"/> -->
      <button type="button" class="btn btn-primary" @click="getLeaderboardData">Search</button>
    </div>
     <b-table
        ref="selectableTable"
        class="ahj-table"
        selectable
        :select-mode="'single'"
        selected-variant=""
        hover
        outlined
        small
        borderless
        @row-clicked="onRowClicked"
        :fields="fields"
        :items="this.apiData ? this.apiData : undefined"
        :busy="this.Loading"
        show-empty
      >
      <template #cell(Rank)="data">
        {{ data.index + 1 }}
      </template>
      <template #cell(Photo)="data">
        <div>
          <img  v-if="checkNotEmpty(data.value)" class='leaderboard-photo' :src="data.value" />
          <img  v-else class='leaderboard-photo' src="../assets/images/profile-image-default.jpeg" />
        </div> 
      </template>
      
      <template #cell(Title)="data">
        <div v-if="checkNotEmpty(data.value)">{{data.value}}</div>
        <div v-else>-</div>
      </template>
      <template #empty>
        <div class="ahj-not-found-text">
          No Users Found
        </div>
      </template>
        <template #table-busy>
          <div class="text-center text-primary my-2">
            <b-spinner class="align-middle"></b-spinner>
            <strong>&nbsp; Loading...</strong>
          </div>
        </template>
      </b-table>
  </div>
</template>

<script>
import axios from "axios";
import constants from "../constants.js";
export default {
    data() {
        return {
          fields: [
            {
              key: 'Rank',
              thStyle: { width: "60px" },
              class: "text-center",
              thClass: ".col-field-styling"
            },
            {
              key: "Photo",
              label: "User",
              thStyle: { width: "80px" },
            },
            {
              key: "Username",
              label: "",
              thStyle: { width: "274px" },
              class: "text-left",
              thClass: ".hidden_header"
            },
            {
              key: "ContactID.Title.Value",
              label: "Title",
              thStyle: { width: "300px" },
              class: "text-left",
              thClass: ".col-field-styling"
            },
            {
              key: "SignUpDate",
              label: "Signup Date",
              thStyle: { width: "274px" },
              class: "text-left",
              thClass: ".col-field-styling"
            },
            {
              key: "ContactID.Address.StateProvince.Value",
              label: "State",
              thStyle: { width: "274px" },
              class: "text-center",
              thClass: ".col-field-styling"
            },
            {
              key: "ContactID.Address.Country.Value",
              label: "Country",
              thStyle: { width: "274px" },
              class: "text-center",
              thClass: ".col-field-styling"
            },
            {
              key: "AcceptedEdits",
              label: "Accepted Edits",
              thStyle: { width: "274px" },
              class: "text-center",
              thClass: ".col-field-styling"
            },
            {
              key: "CommunityScore",
              label: "Community Score",
              thStyle: { width: "274px" },
              class: "text-center",
              thClass: ".col-field-styling"
            },
          ],
          SearchOption: 'CommunityScore',
          StateProvince: null,
          Country: ['USA'],
          Loading: true,
          apiData: []
        }
    },
    computed: {
      Photo(){
        return 'https://cdn.vox-cdn.com/thumbor/4QtOwnOxCdwESvt1-CpQSTZvHHA=/1400x1400/filters:format(jpeg)/cdn.vox-cdn.com/uploads/chorus_asset/file/19932738/1206292068.jpg.jpg';
      }
    },
    methods: {
      getLeaderboardData(){
        this.Loading = true;
        let query = constants.API_ENDPOINT + "leaderboard/";
            axios.get(query,
                {
                  params: {
                    'StateProvince': this.StateProvince,
                    'Country': this.Country,
                    'SearchOption': this.SearchOption
                  }
                })
                .then( (response) => {
                    this.apiData = response.data;
                    this.Loading = false;
                })
                .catch(() => {
                });
      },
      checkNotEmpty(data){
        return data !== '';
      },
      onRowClicked(rowItem){
        this.$router.push({ name: 'view-profile', params: { username: rowItem.Username }})
      }
    },
    mounted() {
      this.getLeaderboardData();
    },
    watch: {
   }
}
</script>

<style scoped>
h1 {
  margin-bottom: 5%;
}

.leaderboard-photo {
    border-radius: 10px;
    border: 1.5px solid lightgray;
    object-fit: cover;
    height: 60px;
    width: 60px;
}

.leaderboard-input{
  display: flex;
  justify-content: flex-start;
  align-items: flex-start;
  margin-bottom: 2%;
  width: 50%;
}

.leaderboard-input > * {
  flex: 2;
  margin-right: 10px;
}


</style>
