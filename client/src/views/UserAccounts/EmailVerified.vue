<template>
  <div id="email-verified-component-container">
    <b-row align-h="center" align-v="center" class="top-buffer">
        <b-col cols="11" md="8" lg="6" xl="4">
        <div class="shadow px-5 py-3 bg-white rounded" id="email-verified-container">
            <span id="email-verified-title">
                Account Activation
            </span>
            <template v-if="this.Loading">
                <div>
                    {{this.statusText}}
                </div>
            </template>
            <template v-else>
                <div id="icon-container">
                    <b-icon class="envelope-icon" icon="check2-circle" font-scale="7.5"></b-icon>
                </div>
                <div id="confirmation-text">
                    {{this.statusText}}
                </div>
            </template>
        </div>
        </b-col>
    </b-row>
  </div>
</template>

<script>
import axios from "axios";
import constants from "../../constants.js";

export default {
    data() {
        return {
            uid: "",
            token: "",
            Loading: true,
            statusText: ""
        }
    },
    methods: {
        ActivateEmail() {
            this.statusText = "Activating your account... Please Wait...";
            axios.post(constants.API_ENDPOINT + "auth/users/activation/", {
                "uid": this.$route.params.uid,
                "token": this.$route.params.token
            }).then(() => {
                this.Loading = false;
                this.statusText = "Account Activated! Redirecting to login page...";
                let that = this;
                setTimeout(function(){ that.ChangePage(); }, 3000); // Give user time to read their account was activated.
            }).catch(() => {
                this.statusText = "Could not activate account. Invalid reset link or server error.";
            })
        },
        ChangePage() {
            this.$router.push({name: 'login'})
        }
    },
    mounted() {
        this.ActivateEmail();
    }
}
</script>

<style scoped>

a {
    color: #277bcd;
    font-size: 1em;
    font-weight: bold;
}

#email-verified-component-container {
    background-color: #f7f7f7;
}

#email-verified-title {
    font-size: 2.5em;
    color: #7a7775;
}

.form-spacing {
    display: block;
    padding-bottom:.5rem;
}

.top-buffer { 
    margin-top:10%; 
}

#confirmation-text {
    display: inline-block;
    margin-top: 1.5em;
    font: 20px Helvetica;
    text-align: center;
}
#icon-container {
    margin-top: 1.5em;
    display: flex;
    align-items: center;
    justify-content: center;
    color: green;
    animation-name: success;
    animation-duration: 1.2s;
    animation-iteration-count: 1;
    animation-timing-function: ease-out;
}

@keyframes success {
    0% {
        color: white;
        transform: rotate(0deg);
        opacity: 0;
    }
    90% {
        transform: rotate(370deg);
        opacity: 1;
    }
    100% {
        transform: rotate(360deg);
        color: green;
    }
}

</style>
