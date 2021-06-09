<template>
    <div>
        <h1>Change Password</h1>
        <form @submit.prevent id="password-reset-form">
            <div class="form-spacing">
                <label>Current Password</label>
                <b-form-input size="lg" class="form__input" type="password" placeholder="Current Password" required v-model="CurrentPassword" :state="$v.CurrentPassword.$dirty ? (!$v.CurrentPassword.$error) : null" alt="Current Password"></b-form-input>
            </div>
            <div v-if="$v.CurrentPassword.$dirty">
                <div class="error" v-if="!$v.CurrentPassword.required">Current password is required.</div>
                <div class="error" v-if="this.ErrorMessage === 'Invalid password.'">Invalid current password.</div>
            </div>
            <div class="form-spacing">
                <label>New Password</label>
                <b-form-input size="lg" class="form__input" type="password" placeholder="New Password" required v-model="NewPassword" :state="$v.NewPassword.$dirty ? (!$v.NewPassword.$error) : null" alt="New Password"></b-form-input>
            </div>
            <div v-if="$v.NewPassword.$dirty">
                <div class="error" v-if="!$v.NewPassword.required">New password is required.</div>
                <div class="error" v-if="!$v.NewPassword.minLength && NewPassword !== ''">Password must be at least {{ $v.NewPassword.$params.minLength.min }} characters.</div>
                <div class="error" v-if="(!$v.NewPassword.ContainsNumOrSpecialChar || !$v.NewPassword.ContainsLetter) && NewPassword !== ''">Atleast one letter and one number/symbol.</div>
                <div class="error" v-if="this.ErrorMessage === 'This password is too common.'">Inputted password too common.</div>
            </div>
            <div v-else>
                <b-form-text id="input-live-help">Must have 8 or more characters with atleast one letter and one number/symbol.</b-form-text>
            </div>
            <div class="form-spacing">
                <label>Confirm New Password</label>
                <b-form-input size="lg" class="form__input" type="password" placeholder="Confirm New Password" required v-model="ReNewPassword" :state="$v.ReNewPassword.$dirty ? (!$v.ReNewPassword.$error) : null" alt="Retyped new password"></b-form-input>
            </div>
            <div v-if="$v.ReNewPassword.$dirty">
                <div class="error" v-if="!$v.ReNewPassword.sameAsPassword">Passwords must be identical.</div>
            </div>

            <b-button id="password-reset-button" @click="ChangePassword" :disabled="(this.$v.$invalid && this.$v.$dirty) || this.SubmitStatus === 'PENDING'" block pill variant="primary">
                Change Password
            </b-button>
            <div class="forgot-password-link">
                <a href="#/password_reset" v-on:click="$router.push({name: 'password_reset'})">
                    Forgot your password?
                </a>
            </div>
            <h4 class="api-status-text" v-if="this.SubmitStatus === 'PENDING'"> Updating password... </h4>
            <h4 class="api-status-text success" v-if="this.SubmitStatus === 'OK'"> Your password has been updated!</h4>
            <h4 class="api-status-text error" v-if="this.SubmitStatus === 'ERROR'"> Error with submitting new password.</h4>
        </form>
    </div>
</template>

<script>
import axios from "axios";
import constants from "../../../constants.js";
import { required, minLength, sameAs } from 'vuelidate/lib/validators';

const ContainsNumOrSpecialChar = constants.NUM_OR_SPECIAL_CHAR;
const ContainsLetter = constants.CONTAINS_LETTER;

export default {
    data() {
            return {
                CurrentPassword: '',
                NewPassword: '',
                ReNewPassword: '',
                SubmitStatus: '',
                ErrorMessage: ''
            }
        },
    methods: {
        ChangePassword(){
            this.$v.$touch();
            if (!this.$v.$invalid) {
                this.SubmitStatus = "PENDING";
                axios.post(constants.API_ENDPOINT + "auth/users/set_password/", {
                        "new_password": this.NewPassword,
                        "re_new_password": this.ReNewPassword,
                        "current_password": this.CurrentPassword
                    },
                    {
                    headers: {
                        Authorization: this.$store.state.loginStatus.authToken
                    }
                    }).then(() => {
                        this.SubmitStatus = 'OK';
                    }).catch(error => {
                  this.SubmitStatus = 'ERROR';
                  if ("current_password" in error.response.data)
                    this.ErrorMessage = error.response.data.current_password[0]
                  else if ("new_password" in error.response.data)
                    this.ErrorMessage = error.response.data.new_password[0]
                });
            }
        },
    },
    validations: {
        CurrentPassword: {
            required
        },
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
    margin: 0;
    padding: 0;
    font-size: 18px;
    font-weight: 800;
}
.form-spacing {
    margin: 1.3em auto 0;
    display: flex;
    justify-content: space-between;
}
.form-spacing > label {
    flex: 30%;
    margin-right: 1em;
}
.form__input {
    flex: 70%;
    width: 100px !important;
    margin-left: 1em;
}
.forgot-password-link {
    margin-top: 1em;
}
#password-reset-button {
    border: none;
    background-color: #ff8c00 !important;
    width: 60%;
    margin: 1.3em auto 0;
}

.api-status-text {
    text-align: center;
    margin-top: 20px;
}
.success {
    color: green;
}
.error {
    color: red;
}

@media (max-width: 650px){
    h1 {
        font-size: 2.2rem;
    }
    .form-spacing > label {
        margin-right: 0.5em;
        font-size: 1rem;
    }
    .form__input { 
        font-size: 1rem;
    }
}
</style>