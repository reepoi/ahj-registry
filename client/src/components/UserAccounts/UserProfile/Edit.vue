<template>
    <div>
        <p>Changed the <b>{{EditedField}}</b> field on {{ahjName}} AHJ's <b>{{EditedDataType}}</b> data.</p>
        <p>
            <span class="row-element">Old Value: <span class="red">{{ActivityData.OldValue}}</span></span>  
            <span>New Value: <span class="green">{{ActivityData.NewValue}}</span></span>
        </p>
        <p>
            <span class="row-element">Status: 
                <b-icon icon="circle-fill" class="circle-icon" :class="StatusColor"></b-icon> 
                <span :class="StatusColor">{{Status}}</span>
            </span>
            <span>
                <span v-if="Status === 'Accepted'">Accepted by:</span> <span v-if="Status === 'Rejected'">Rejected by: </span> 
                <span v-if="this.ActivityData.ApprovedBy">{{ReviewedByFullName}}</span>
            </span>
        </p>
    </div>
</template>

<script>
import axios from "axios";
import constants from "../../../constants.js";
export default {
    data() {
        return {
            ahjName: ''
        }
    },
    props: ['ActivityData'],
    computed: {
        EditedField(){
            return this.SplitByCapital(this.ActivityData.SourceColumn);
        },
        EditedDataType(){
            return this.SplitByCapital(this.ActivityData.SourceTable);
        },
        Status(){
            if (this.ActivityData.ReviewStatus === 'A') return "Accepted";
            else if (this.ActivityData.ReviewStatus === 'R') return "Rejected";
            return "Pending";
        },
        StatusColor(){
            if (this.ActivityData.ReviewStatus === 'A') return "green";
            else if (this.ActivityData.ReviewStatus === 'R') return "red";
            return "grey";
        },
        ReviewedByFullName() {
            return `${this.ActivityData.ApprovedBy.ContactID.FirstName.Value} ${this.ActivityData.ApprovedBy.ContactID.LastName.Value}`;
        },
        AHJName(){
            return this.ahjName;
        }
    },
    methods: {
        SplitByCapital(string){
            return string.replace(/([A-Z]+)/g, ' $1').trim();
        },
        FindAHJName(AHJPK){
            let query = constants.API_ENDPOINT + "ahj-one/";
            axios.get(query,
                {
                  params: {
                    'AHJPK': AHJPK
                  },
                  headers: {
                    Authorization: `${this.$store.getters.authToken}`
                  }
                })
                .then( (response) => {
                    this.ahjName = response.data[0].AHJName.Value;
                })
                .catch(() => {
                });
        }
    },
    mounted(){
        this.FindAHJName(this.ActivityData.AHJPK);
    }
}
</script>

<style scoped>
.red {
    color: red;
}
.green {
    color: green;
}
.grey {
    color: grey;
}
.circle-icon {
    height: 0.8em;
    width: 0.8em;
    margin-right: 0.4em;
}
.row-element {
    margin-right: 5%;
}
</style>