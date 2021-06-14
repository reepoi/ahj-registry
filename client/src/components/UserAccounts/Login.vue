<template>
  <div id="login-component-container">
    <b-row align-h="center" align-v="center" id="login-component-row">
        <b-col cols="11" md="8" lg="6" xl="4">
        <div class="login-form-container shadow py-3 bg-white rounded">
            <form @submit.prevent id="login-form">
                <div class="vertical-center">
                    <span id="login-form-title">
                        Login
                    </span>

                    <b-alert v-model="showDismissibleAlert" variant="danger" dismissible> {{this.errorMessage}} </b-alert>

                    <div class="form-spacing">
                        <label class="form-label">Email</label>
                        <b-form-input size="lg" type="text" class="form-input" v-model="Email" placeholder="Email" :state="($v.Email.$dirty & $v.Email.$error) ? !$v.Email.$error : null" alt="Email"></b-form-input>
                    </div>
                    <div v-if="$v.Email.$dirty">
                        <div class="error" v-if="!$v.Email.required">Email is required.</div>
                        <div class="error" v-if="!$v.Email.ValidEmail && Email !== ''">Incorrect email format. Ex: example@example.com</div>
                    </div>

                    <div class="form-spacing" data-validate="Enter password">
                        <div id="password-label-section">
                            <label class="form-label">Password</label>
                            <a id="forgot-password-link" href="#/password_reset" v-on:click="$router.push({name: 'password_reset'})">
                                Forgot password?
                            </a>
                        </div>
                        <b-form-input size="lg" type="password" class="form-input" v-model="Password" v-model.trim="$v.Password.$model" :state="($v.Password.$dirty & $v.Password.$error) ? !$v.Password.$error : null" placeholder="Password" alt="Password"></b-form-input>
                    </div>
                    <div v-if="$v.Password.$dirty">
                        <div class="error" v-if="!$v.Password.required">Password is required.</div>
                    </div>
                    
                    <b-button id="login-button" block pill variant="blue" @click="login">
                        Login
                    </b-button>

                    <h4 class="api-status-text text-center" v-if="this.SubmitStatus === 'PENDING'"> Logging you in... </h4>

                    <div class="text-center">
                        <span> Don’t have an account? </span>
                        <a href="#/register">
                            Sign Up
                        </a>
                    </div>
                </div>
            </form>
        </div>
        </b-col>
    </b-row>
  </div>
</template>

<script>
import axios from "axios";
import constants from "../../constants.js";
import { required } from 'vuelidate/lib/validators'

const ValidEmail = constants.VALID_EMAIL;

export default {
    data() {
        return {
            Email: "",
            Password: "",
            showDismissibleAlert: false,
            SubmitStatus: "",
            errorMessage: ""
        }
    },
    methods: {
        login() {
            this.$v.$touch();
            if (!this.$v.$invalid) {
                this.SubmitStatus = 'PENDING';
                axios.post(constants.API_ENDPOINT + "auth/token/login/", {
                    "Email": this.Email,
                    "password": this.Password
                    }, {
                    headers: {
                        'Authorization': `${this.$store.getters.authToken}`
                    }
                }).then(response => {
                    this.SubmitStatus = 'OK';
                    let loginStatus = {
                        authToken: "Token " + response.data["auth_token"],
                        Username: response.data.User['Username'],
                        Photo: response.data.User['Photo'],
                        MaintainedAHJs: response.data.User['MaintainedAHJs'],
                        IsSuperuser: response.data.User['IsSuperuser']
                    }
                    this.$router.push({name: 'ahj-search'})
                    this.$store.commit("changeUserLoginStatus", loginStatus);
                }).catch(error => {
                    this.SubmitStatus = 'ERROR';
                    let response = error.response
                    if (response && response.data.non_field_errors)
                        this.errorMessage = response.data.non_field_errors[0];
                    else
                        this.errorMessage = "Something went wrong with logging you in."
                    this.showDismissibleAlert = true;
                    });   
            }
        }
    },
    validations: {
        Email: {
            required,
            ValidEmail
        },
        Password: {
            required
        },
    },
}
</script>

<style scoped>
label {
    margin: 0;
    padding: 0;
}

a {
    color: #196dd6;
    font-size: 1rem;
    font-weight: bold;
}

#login-component-row{
    width: 100%;
    margin-top:10%; 
}

#login-form {
    width: 80%;
    margin: auto;
}

#login-form-title {
    display: inline-block;
    margin-top: 0.8em;
    margin-bottom: 0.2em;
    color: #6b6b6b;
    font: 2.5em Helvetica;
}

.form-label {
    font-size: 1.3rem;
}

.form-spacing {
    display: block;
    margin-top: 1em;
}

.form-input {
    padding: 1em .8em;
    border: 0.5px solid #c0c1c2;
    line-height: 10;
    font: 1.3rem Helvetica;
}

#forgot-password-link {
    font-size: 1rem;
}

#password-label-section {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
}

#login-button {
    font-size: 1.4rem;
    font-weight: bold;
    width: 60%;
    color: white;
    margin: 1em auto;
    background-color: #ff8c00 !important;
}

.api-status-text {
    text-align: center;
    margin: 1em;
}

.error {
    color: #dc3545;
}

@media (max-width: 500px){
    #login-form {
        width: 90%;
    }
}

</style>
