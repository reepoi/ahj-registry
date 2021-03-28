<template>
    <div>
        <h1>API</h1>
        <div>
            <h4 id="api-description-text">Our API makes searching and filtering AHJs by location, AHJ ID, Building Code type, and many other attributes an easy process. Documentation for our API is still in the works.</h4>
            <b-button id="documentation-button" class="button" disabled block pill variant="primary">
                Go to Documentation
            </b-button>
        </div>
        <b-button id="generate-token-button" class="button" @click="GenerateAPIToken" :disabled="this.SubmitStatus === 'PENDING'" block pill variant="primary">
            Generate New Token
        </b-button>
        <p>Note: One token per account. <b> Generating a new token will destroy any older tokens.</b></p>
        
        <h4 class="api-status-text" v-if="this.generatedAPIToken && this.SubmitStatus === 'OK'">Your new API token: <span>{{this.APIToken}}</span></h4>
        <h4 class="api-status-text" v-if="this.SubmitStatus === 'PENDING'"> Generating Token... </h4>
        <h4 class="api-status-text error" v-if="this.SubmitStatus === 'ERROR'"> Something went wrong with generating your API token. </h4>
    </div>
</template>

<script>
import axios from "axios";
import constants from "../../../constants.js";
export default {
    data() {
        return {
            APIToken: "",
            generatedAPIToken: false,
            SubmitStatus: ""
        }
    },
    methods: {
        GenerateAPIToken() {
            this.SubmitStatus = "PENDING";
            axios.get(constants.API_ENDPOINT + "auth/api-token/create/", 
                        {
                            headers: {
                                Authorization: this.$store.getters.authToken
                            }
                        }
                    )
                    .then((response) => {
                        this.SubmitStatus = "OK";
                        this.APIToken = response.data['auth_token'];
                        this.generatedAPIToken = true;
                    })
                    .catch(() => {
                        this.SubmitStatus = "ERROR";
                    });
        }
    }
}
</script>

<style scoped>
.button {
    width: 30%;
    min-width: 180px;
    border: none;
    background-color: #ff8c00 !important;
}
#documentation-button {
    margin-bottom: 50px;
}
#generate-token-button {
    margin-bottom: 5px;
}
.api-status-text {
    margin-top: 30px;
}
.error{
    color: red;
}
@media (max-width: 1000px){
    #api-description-text {
        font-size: 1.2rem;
    }
}
@media (max-width: 650px){
    h1 {
        font-size: 2.2rem;
    }
    .api-status-text {
        font-size: 1rem;
    }
    #api-token-text span {
        font-size: .9rem;
    }
}
</style>