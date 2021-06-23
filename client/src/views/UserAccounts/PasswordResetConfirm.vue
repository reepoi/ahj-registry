<template>
  <div id="password-reset-component-container">
    <b-row align-h="center" align-v="center" class="top-buffer">
        <b-col cols="11" md="8" lg="6" xl="4">
        <div class="shadow px-5 py-3 bg-white rounded" id="password-reset-form-container">
            <form @submit.prevent>
                <div class="vertical-center">
                    <span id="password-reset-form-title">
                        Reset Password
                    </span>
                    <template v-if="this.Loading">
                        <div class="form-spacing">
                            <label class="form-label">Password</label>
                            <b-form-input size="lg" class="form-input" type="password" v-model="NewPassword" placeholder="Password" :state="$v.NewPassword.$dirty ? (!$v.NewPassword.$error || backendPasswordError !== null) : null" alt="Password"></b-form-input>
                        </div>
                        <div v-if="$v.NewPassword.$dirty">
                            <div class="error" v-if="!$v.NewPassword.required">Password is required.</div>
                            <div class="error" v-if="!$v.NewPassword.minLength && NewPassword !== ''">Password must be at least {{ $v.NewPassword.$params.minLength.min }} characters.</div>
                            <div class="error" v-if="(!$v.NewPassword.ContainsNumOrSpecialChar || !$v.NewPassword.ContainsLetter) && NewPassword !== ''">Atleast one letter and one number/symbol.</div>
                            <div class="error" v-if="backendPasswordError">Entered password error: {{backendPasswordError}}</div>
                        </div>

                        <div class="form-spacing">
                            <label class="form-label">Confirm Password</label>
                            <b-form-input size="lg" class="form-input" type="password" v-model="ReNewPassword" placeholder="Confirm Password" :state="$v.ReNewPassword.$dirty ? (!$v.ReNewPassword.$error && ReNewPassword !== '') : null" alt="Retyped New Password"></b-form-input>
                        </div>
                        <div v-if="$v.ReNewPassword.$dirty">
                            <div class="error" v-if="!$v.ReNewPassword.sameAsPassword">Passwords must be identical.</div>
                        </div>
                        <b-button id="password-reset-button" block pill variant="blue" @click="ResetPassword">
                            Reset Password
                        </b-button>
                    </template>
                    <template v-else>
                        <div id="icon-container">
                            <b-icon class="envelope-icon" icon="check2-circle" font-scale="7.5"></b-icon>
                        </div>
                        <div id="confirmation-text">
                            Your password was reset! 
                        </div>
                    </template>
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
import { required, minLength, sameAs } from 'vuelidate/lib/validators';


const ContainsNumOrSpecialChar = constants.NUM_OR_SPECIAL_CHAR;
const ContainsLetter = constants.CONTAINS_LETTER;

export default {
    data() {
        return {
            uid: "",
            token: "",
            NewPassword: "",
            ReNewPassword: "",
            Loading: true,
            backendPasswordError: null
        }
    },
    methods: {
        ResetPassword() {
            this.$v.$touch();
            if (!this.$v.$invalid) {
                let data = {
                    "uid": this.$route.params.uid,
                    "token": this.$route.params.token,
                    "new_password": this.NewPassword,
                    "re_new_password": this.ReNewPassword
                }
                axios.post(constants.API_ENDPOINT + "auth/users/reset_password_confirm/", data)
                .then(() => {
                    this.Loading = false;
                }).catch(error => {
                    if (error.response.data.new_password){
                        this.backendPasswordError = error.response.data.new_password[0];
                    }
                    else if (error.response.data.token){
                        alert("Invalid password reset link.");
                    }
                    else {
                        alert("Error with resetting password.");
                    }
                })
            }
        },
    },
    validations: {
        NewPassword: {
            required,
            minLength: minLength(8),
            ContainsNumOrSpecialChar,
            ContainsLetter
        },
        ReNewPassword: {
            sameAsPassword: sameAs('NewPassword')
        }
  }
}
</script>

<style scoped>

label {
    padding:0;
    margin:0;
}

#password-reset-component-container{
    background-color: #f7f7f7;
}

.top-buffer { 
    margin-top:10%; 
}

#password-reset-form-title {
    display: inline-block;
    margin-top: 0.8em;
    margin-bottom: 0.2em;
    color: #6b6b6b;
    font: 2.2rem Helvetica;
}

.form-spacing {
    display: block;
    margin-top: 1em;
}

.form-label {
    font-size: 1.3rem;
}

.form-input {
    padding: 1em .8em;
    border: 0.5px solid #c0c1c2;
    line-height: 10;
    font: 1.3rem Helvetica;
}

#password-reset-button {
    font-size: 1.3rem;
    font-weight: bold;
    color: white;
    width: 60%;
    background-color: #ff8c00 !important;
    margin: 1em auto 0em;
}

#confirmation-text {
    display: block;
    margin-top: 1.5em;
    font: 20px Helvetica;
    text-align: center;
}

.error {
    color: red;
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
