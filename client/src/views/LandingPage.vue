<template>
  <div class="landing-page-container">
    <!-- Hero Section -->
    <div id="hero-section">
        <div id="hero-text">
            <h1 id="hero-headline">Building permits made easy</h1>
            <h3 id="hero-headline-support-text">The AHJ Registry makes finding AHJs simple 
                through its search tools and API. <span id="lead-extra-text">Finding building 
                code requirements has never been easier. </span>
            </h3>
            <b-button variant="primary" id="hero-section-button" size="md" @click="$router.push({ name: 'register' })">Create Account</b-button>
            <div id="hero-email-section">
                <b-form-input type="text" placeholder="Email" size="lg" id="hero-email-input" required v-model="Email"></b-form-input>
                <b-button variant="primary" id="hero-email-button" @click="SendToRegisterPage">Get Started</b-button>
            </div>
            <div v-if="$v.Email.$dirty">
                <div class="error" v-if="!$v.Email.required">Email is required.</div>
                <div class="error" v-if="!$v.Email.ValidEmail && Email !== ''">Incorrect email format. Ex: example@example.com</div>
            </div>
        </div>
    </div>
    
    <!-- Client Section -->
    <div id="client-section">
        <img v-for="client in clientPhotos" :key="client" :src="require('@/assets/' + clientPhotoLocation + client + '')" />
    </div>

    <!-- About Section -->
     <div id="about-section">
        <h2 id="about-section-header">What is the AHJ Registry?</h2>
        <h4>The AHJ Registry contains the building permit and contact information for most 
            AHJs within the United States. The registry is founded upon a collection of data 
            provided by NREL and is kept updated through crowd-sourced edits. <br> <br>
            The registry has a 97% accuracy rate with building permit requirements.
        </h4>
         <!-- video section div to specify max height, videowrapper and iframe for responsiveness trick -->
        <!-- <div id="video-section">
            <div id="videowrapper">
                <iframe width="560" height="315" src="https://www.youtube.com/embed/BrXDBxBssgU?start=325" frameborder="0" allowfullscreen></iframe>
            </div>
        </div> -->
    </div>

    <!-- Feature Sections -->
    <feature-section headerText="AHJ Map Search Tool" 
                    paragraphText="If you want to see AHJ office locations and their jurisdiction lines on a map, check out our AHJ search tool."
                    buttonText="Jump to Search Tool"
                    buttonPageLink="ahj-search"
                    pictureSide="right"
                    imgSrc="images/LandingPage/ComponentPictures/partial_map.png"
                    ></feature-section>
    <feature-section headerText="Our API" 
                    paragraphText="Our API makes searching and filtering AHJs by location, AHJ ID, Building Code type, and many other attributes an easy process. Create an account to request an API token"
                    buttonText="View Documentation"
                    buttonPageLink="login"
                    pictureSide="left"
                    imgSrc="images/LandingPage/ComponentPictures/API_code.png"
                    ></feature-section>
    <feature-section headerText="Edits" 
                    paragraphText="Community-sourced edits is what keeps the AHJ registry updated.
                    Users submit edits on AHJ pages and AHJ officials will accept or reject edits depending on their accuracy."
                    pictureSide="right"
                    imgSrc="images/LandingPage/ComponentPictures/edit_icon.png"
                    ></feature-section>

    <!-- Account Description Section -->
    <div id="account-description-section">
        <h2>Create an Account</h2>
        <div id="account-feature-list">
            <account-feature-description headerText="API Access" 
                    paragraphText="Gain throttled access to our API when you request an API token"
                    imgSrc="images/LandingPage/CreateAccountIcons/lock.png"
                    ></account-feature-description>
            <account-feature-description headerText="Edit Access" 
                        paragraphText="Submit / accept edit requests to keep the registry up to date"
                        imgSrc="images/LandingPage/CreateAccountIcons/colab.png"
                        ></account-feature-description>
            <account-feature-description headerText="Leaderboards" 
                        paragraphText="View nationwide leaderboards to see the registry's top contributors"
                        imgSrc="images/LandingPage/CreateAccountIcons/leaderboard.png"
                        ></account-feature-description>
        </div>
        <b-button variant="primary" id="account-description-button" size="lg" @click="$router.push({ name: 'register' })">Create Account</b-button>
    </div>
  </div>
</template>

<script>
import { required } from 'vuelidate/lib/validators';
import constants from "../constants.js";
import FeatureSection from "../components/LandingPage/FeatureSection.vue";
import AccountFeatureDescription from "../components/LandingPage/AccountFeatureDescription.vue";
// Animate on scroll library (used mainly in FeatureSelection sections)
import AOS from 'aos';
import 'aos/dist/aos.css';

AOS.init();

const ValidEmail = constants.VALID_EMAIL;

export default {
    data() {
        return {
            Email: '',
            clientPhotos: ['titan_solar.png', 'aurora.jpg', 'solar_app.png', 'raise_green.png', 
            'ipsun_solar.jpg', 'solar_power_of_oklahoma.jpg', '17_terawatts.jpg'],
            clientPhotoLocation: "images/LandingPage/clients/",
        }
    },
    computed: {
    },
    methods: {
        SendToRegisterPage(){
            this.$v.$touch();
            if (!this.$v.$invalid) {
                let email = this.Email;
                this.$router.push({ name: 'register', params: { email }});
            }
        }
    },
    validations: {
        Email: {
            required,
            ValidEmail
        }
    },
    components: {
    "feature-section": FeatureSection,
    "account-feature-description": AccountFeatureDescription
  }
}
</script>

<style scoped>

h1 {
    font-size: 4.5rem;
}

h2 {
    font-size: 4rem;
}

#hero-section {
    background: url('~@/assets/images/LandingPageMain.png') no-repeat center/cover;
    width: 100%;
    height: 90vh;
    overflow: hidden;
    position: relative;
    background-position: bottom 0px left 500px;
}

#hero-text {
    margin-left: 12%;
    margin-top: 7%;
}

#hero-text h3{
    width: 45%;
    margin-bottom: 1em;
}

#hero-headline {
    width: 600px;
    margin-bottom: 0.25em;
}

.error {
    color: #dc3545;
}

#hero-email-section {
    margin-top: 25px;
    display: flex;
    width: 50%;
}
#hero-email-section > * {
    font-size: 1.2rem;
    border-radius: 0.5em;
}

#hero-email-input {
    width: 50%;
    margin-right: 1em;
    border-width: 0.15em;
}

#hero-email-button {
    font-family: "Segoe UI";
    font-style: bold;
    width: 8em;
    padding: 0;
    font-weight: 700;
}

#hero-section-button {
    display: none;
}

#client-section {
    display: flex;
    padding: 40px 0px;
    width: 92%;
    margin: auto;
}

#client-section > * {
    max-height: 13vh;
    max-width: 12.5vw;
    flex: 1;
    object-fit: contain; /* always keep the aspect ratio the same */
    margin-right: 1vw;
    width: 100%;
}

#about-section > * {
    text-align: center;
    width: 60%;
    margin: 50px auto 50px;
}

#about-section-header {
    margin-bottom: 0.8em;
}

#video-section {
    width: 100%;
    height: 400px;
}

#videowrapper {
  position: relative;
  height: 0;
  width: 100%;
  padding-top: 56.25%; /* 16:9 Aspect Ratio (divide 9 by 16 = 0.5625) */
}

#videowrapper iframe {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    width: 40%;
    height: 40%;
    border: 0;
    margin-left: auto; 
    margin-right: auto; 
}

#account-description-section {
    margin: 200px auto 100px;
    display: flex;
    flex-direction: column;
}

#account-description-section > h2{
    margin: 0px auto 75px;
}

#account-description-button {
    margin: auto;
}

#account-feature-list {
    display: flex;
    justify-content: space-between;
    width: 70%;
    margin: 0px auto 50px;
}

@media (max-width: 1000px){
    h1 {
        font-size: 4.5rem;
    }
    h2 {
        font-size: 3rem;
    }
    h4 {
        font-size: 1.3rem;
    }
    #hero-section {
        height: 80vh;
        background-position: bottom 0px left 50px;
    }
    #hero-text > * {
        text-align: center;
    }
    #hero-text {
        margin-left: 0%;
    }
    #hero-text h1 {
        font-size: 4.5rem;
        margin-top: 15vh;
    }
    #hero-text h3{
        font-size: 1.5rem;
        width: 65%;
        margin: auto;
    }
    #hero-headline {
        width: 80%;
        margin: 0rem auto 4rem;
    }
    #hero-section-button {
        width: 50%;
        margin: auto;
        display: block;
        border-radius: 0.5em;
        margin-top: 5vh;
    }
    #hero-email-section {
        display: none;
    }
    #client-section {
        flex-wrap: wrap;
        justify-content: center;
        padding: 10px 0px;
    }
    #client-section > *{
        max-height: 130px;
        max-width: 170px;
        margin-top: 20px;
        margin-right: 10px;
        padding: 20px 0px;
    }
    #about-section > * {
        width: 80%;
    }
    #about-section h4 {
        width: 70%;
    }
    #videowrapper iframe {
        width: 70%;
        height: 70%;
    }
    #video-section {
        height: 350px;
    }
    #account-feature-list {
        justify-content: center;
        margin-bottom: 20px;
        padding-right: 0px;
        width: 90%;
    }
    #account-description-section {
        margin-top: 50px;
    }
}

@media (max-width: 650px){
    h1 {
        font-size: 3rem;
    }
    h2 {
        font-size: 2.5rem;
    }
    h4 {
        font-size: 1.25rem;
    }
    #hero-text h1 {
        font-size: 2.8rem;
    }
    #hero-text h3{
        width: 80%;
        margin: 5vh auto 0;
    }
    #hero-headline {
        width: 90%;
        margin: 0rem auto 2rem;
    }
    #lead-extra-text {
        display: none;
    }
    #hero-section-button {
        width: 60%;
        margin-top: 10vh;
    }
    #client-section > *{
        max-height: 100px;
        max-width: 130px;
        margin-top: 5px;
    }
    #about-section h4 {
        width: 80%;
    }
    #videowrapper iframe {
        width: 100%;
        height: 100%;
    }
    #video-section {
        width: 80%;
        height: 180px;
    }
    #account-feature-list {
        flex-direction: column;
        align-items: center;
    }
    #account-description-section > h2{
        margin: 50px auto;
        font-size: 2.5rem;
    }
}

</style>
