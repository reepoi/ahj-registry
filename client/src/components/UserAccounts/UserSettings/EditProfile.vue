<template>
    <div class="edit-profile-container">
        <h1 class="setting-title">Edit Profile</h1>
        <template v-if="this.profileInfoLoaded">
            <div class="header">
                <img class="user-photo" src="../../../assets/images/profile-image-default.jpeg">
                <div class="header-user-identifiers" v-if="formFirstNameCapital !== ''">
                    <h2>{{`${formFirstNameCapital} ${formLastNameCapital}`}} </h2>
                </div>
                <div v-else>
                    <h2><b>{{Username}}</b></h2>
                </div>
            </div>
            <form @submit.prevent id="registration-form">
                <div class="form-spacing">
                    <label>Name</label>
                    <div class="flex-row">
                        <b-form-input size="lg" class="form__input" type="text" placeholder="First Name" :state="$v.formFirstNameCapital.$dirty ? !$v.formFirstNameCapital.$error : null" required v-model="formFirstNameCapital" alt="First Name"></b-form-input>
                        <b-form-input size="lg" class="form__input" type="text" placeholder="Last Name" :state="$v.formLastNameCapital.$dirty ? !$v.formLastNameCapital.$error : null" required v-model="formLastNameCapital" alt="Last Name"></b-form-input>
                    </div>
                    
                </div>
                <div v-if="$v.$dirty">
                    <div class="error" v-if="!$v.formFirstNameCapital.required || !$v.formLastNameCapital.required">First and Last name are required.</div>
                </div>
                <div class="form-spacing">
                    <label>Work Phone</label>
                    <b-form-input size="lg" class="form__input" type="text" placeholder="Work Phone" :state="$v.WorkPhone.$dirty ? !$v.WorkPhone.$error : null" v-model="WorkPhone" alt="Work Phone"></b-form-input>
                </div>
                <div v-if="$v.$dirty">
                    <div class="error" v-if="!$v.WorkPhone.PhoneFormat">Incorrect Phone Format. Recommended format: 123-456-7890</div>
                </div>
                <div v-else>
                    <b-form-text id="phone-help-text">Recommended phone format: 123-456-7890</b-form-text>
                </div>
                <div class="form-spacing">
                    <label>Preferred Contact Method</label>
                    <b-form-select v-model="userInfo.PreferredContactMethod" class="search-input" :options="['Email', 'Phone']" />
                </div>
                <div class="form-spacing">
                    <label>Bio</label>
                    <b-form-textarea id="textarea-default" size="sm" rows="3" placeholder="Bio" v-model="userInfo.PersonalBio" alt="Bio"></b-form-textarea>
                </div>
                <div class="form-spacing">
                    <label>URL</label>
                    <b-form-input size="lg" class="form__input" type="text" placeholder="URL" required v-model="userInfo.URL" alt="URL"></b-form-input>
                </div>
                <div class="form-spacing">
                    <label>Job Title</label>
                    <b-form-input size="lg" class="form__input" type="text" placeholder="Job Title" required v-model="userInfo.Title" alt="Job Title"></b-form-input>
                </div>
                <div class="form-spacing">
                    <label>Company Affiliation</label>
                    <b-form-input size="lg" class="form__input" type="text" placeholder="Company Affiliation" required v-model="userInfo.CompanyAffiliation" alt="CompanyAffiliation"></b-form-input>
                </div>
                <b-button id="edit-profile-button" @click="UpdateDatabase" :disabled="this.SubmitStatus === 'PENDING'" block pill variant="primary">
                    Update Profile
                </b-button>
                <h4 class="api-status-text" v-if="this.SubmitStatus === 'PENDING'"> Updating profile... </h4>
                <h4 class="api-status-text success" v-if="this.SubmitStatus === 'OK'"> Your profile information has been updated! </h4>
                <h4 class="api-status-text error" v-if="this.SubmitStatus === 'ERROR'"> Something went wrong with updating your information. </h4>
            </form>
        </template>
        <template v-else>
            <p>Loading...</p>
        </template>
    </div>
</template>

<script>
import axios from "axios";
import constants from "../../../constants.js";
import { required } from 'vuelidate/lib/validators';

let PhoneFormat = constants.VALID_PHONE;
export default {
    computed: {
        formFirstNameCapital: {
            get: function () {
                    return this.userInfo.FirstName;
                },
            set: function (newFirstName) {
                if(newFirstName.length < 1) {this.userInfo.FirstName = ''; return}
                this.userInfo.FirstName = this.CapitalizeFirstLetter(newFirstName);
            }
        },
        formLastNameCapital: {
            get: function () {
                    return this.userInfo.LastName;
                },
            set: function (newLastName) {
                if(newLastName.length < 1) {this.userInfo.LastName = ''; return}
                this.userInfo.LastName = this.CapitalizeFirstLetter(newLastName);
            }
        },
        WorkPhone: {
            get: function() {
                return this.userInfo.WorkPhone;
            },
            set: function (newWorkPhone) {
                this.userInfo.WorkPhone = newWorkPhone;
            }
        }
    },
    data() {
            return {
                userInfo: {
                    FirstName: null,
                    LastName: null,
                    PersonalBio: null,
                    URL: null,
                    Title: null,
                    CompanyAffiliation: null,
                    WorkPhone: null,
                    PreferredContactMethod: null
                },
                Username: null,
                Photo: '../../../assets/images/profile-image-default.jpeg',
                SubmitStatus: '',
                profileInfoLoaded: false
            }
        },
  methods: {
      GetUserInfo(){
        let query = constants.API_ENDPOINT + "user-one/" + this.$store.state.loginStatus.Username;
        axios.get(query, {
                headers: {
                    Authorization: `${this.$store.getters.authToken}`
                }
            })
            .then(response => {
              let profileInfo = response.data;
              this.$store.commit("changeCurrentUserInfo", response.data);
              this.UpdateLocalProfileData(profileInfo);
              this.profileInfoLoaded = true;
            })
            .catch(() => {
            });
      },
      UpdateLocalProfileData(StoreProfileData) {
        if (StoreProfileData !== null){
            let that = this;
            Object.keys(that.userInfo).map(function(key, index) {
                    if (StoreProfileData[key])
                        that.userInfo[key] = StoreProfileData[key]
                    index;
                });
            this.userInfo.FirstName = StoreProfileData.ContactID['FirstName'].Value;
            this.userInfo.LastName = StoreProfileData.ContactID['LastName'].Value;
            this.userInfo.URL = StoreProfileData.ContactID['URL'].Value;
            this.userInfo.Title = StoreProfileData.ContactID['Title'].Value;
            this.userInfo.WorkPhone = StoreProfileData.ContactID['WorkPhone'].Value;
            this.userInfo.PreferredContactMethod = StoreProfileData.ContactID['PreferredContactMethod'].Value;
            //this.Photo = StoreProfileData['Photo'];
            this.Username = StoreProfileData['Username'];
        }
      },
      UpdateDatabase(){
        this.$v.$touch();
        if (!this.$v.$invalid) {
            this.SubmitStatus = "PENDING";
            this.WorkPhone = this.FormatPhone(this.WorkPhone);
            // Create deep copy of user info and delete userInfo attributes that are empty
            let userInfo = JSON.parse(JSON.stringify(this.userInfo));
            for (let userAttr in userInfo){
                if (!userInfo[userAttr]){
                    delete userInfo[userAttr];
                }
            }
            axios.post(constants.API_ENDPOINT + "user/update/",
                userInfo,
                {
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `${this.$store.getters.authToken}`
                    }
                }
            )
            .then(() => {
                this.SubmitStatus = "OK";
            })
            .catch(() => {
                this.SubmitStatus = "ERROR";
            });
        }
      },
      CapitalizeFirstLetter(string) {
        return string.charAt(0).toUpperCase() + string.slice(1);
        },
    FormatPhone(phone){
        phone = phone.replaceAll('-',"");
        phone = phone.replaceAll('(',"");
        phone = phone.replaceAll(')',"");
        return `(${phone.slice(0,3)})${phone.slice(3,6)}-${phone.slice(6,10)}`
    }   
  },
  mounted() {
    this.GetUserInfo();
  },
  watch: {
    "$store.state.currentUserInfo": function(newVal) {
        this.UpdateLocalProfileData(newVal);
        this.profileInfoLoaded = true;
    }
  },
  validations: {
        formFirstNameCapital: {
            required
        },
        formLastNameCapital: {
            required
        },
        WorkPhone: {
            PhoneFormat
        }
  },
}
</script>

<style scoped>

.setting-title {
    margin-bottom: 0.5em;
}

label {
    font-size: 18px;
    font-weight: 800;
}

.flex-row {
    flex: 100%;
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
}

#textarea-default {
    font-size: 1.2rem;
}

.form-spacing {
    margin: 20px auto;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}
.form-spacing > label {
    flex: 30%;
}
.form-spacing.form__input {
    flex: 70%;
    margin-left: 1em;
}

.flex-row > * {
    width: 48%;
}
.flex-row > label {
    flex: 10%;
    align-items: center;
    vertical-align: center;
    text-align: left;
}

.user-photo {
  width: 8em;
  border-radius: 8em;
  margin-right: 1em;
}

#edit-profile-button{
    border: none;
    background-color: #ff8c00 !important;
}

.header {
    display: flex;
}

.header-user-identifiers > *{
    margin: 10px;
    padding: 0.5em 0px;
}

.api-status-text {
    text-align: center;
    margin-top: 20px;
}

.error {
    color: red;
}

.success {
    color: green;
}

#phone-help-text {
    font-size: 1rem;
}

@media (max-width: 650px){
    .user-photo {
        width: 5em;
        border-radius: 5em;
        margin-right: 1em;
    }
    .header-user-identifiers h2{
        margin: 5px;
        font-size: 1.5rem;
    }
    .form-spacing {
        flex-direction: column;
    }
    #textarea-default {
        font-size: 1rem;
    }
}

</style>