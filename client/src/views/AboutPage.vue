<template>
  <div class="About-page-container">

    <!-- About Section -->
     <div id="about-section">
        <h2 id="about-section-header">What is the AHJ Registry?</h2>
        <h4>The AHJ Registry contains the building permit and contact information for most 
            AHJs within the United States. The registry is founded upon a collection of data
            provided by NREL and is kept updated through crowd-sourced edits. <br> <br>
            <!-- The registry has a 97% accuracy rate with building permit requirements. -->
        </h4>
        <hr style="width:30%;">
         <!-- video section div to specify max height, videowrapper and iframe for responsiveness trick. Used for our final website. -->
         <div id="video-section">
            <div id="videowrapper">
                <iframe width="560" height="315" src="https://www.youtube.com/embed/d8Fwy-3aR50" frameborder="0" allowfullscreen></iframe>
            </div>
        </div> 
    </div>

    <!-- Client Section -->
    <div id="client-section"> 
        <img v-for="client in clientPhotos" :key="client" :src="require('@/assets' + clientPhotoLocation + '' + client + '')" />
    </div>

    <!-- Features Section (describes main features of AHJ Registry)-->
    <feature-section headerText="AHJ Map Search Tool" 
                    paragraphText="If you want to see AHJ office locations and their jurisdiction lines on a map, check out our AHJ search tool."
                    buttonText="Jump to Search Tool"
                    buttonPageLink="ahj-search"
                    pictureSide="right"
                    imgSrc="/images/AboutPage/ComponentPictures/partial_map.png"
                    ></feature-section>
    <feature-section headerText="Our API" 
                    paragraphText="Our API makes searching and filtering AHJs by location, AHJ ID, Building Code type, and many other attributes an easy process. Create an account to request an API token"
                    buttonText="View Documentation"
                    buttonPageLink="login"
                    pictureSide="left"
                    imgSrc="/images/AboutPage/ComponentPictures/API_code.png"
                    ></feature-section>
    <feature-section headerText="Edits" 
                    paragraphText="Community-sourced edits is what keeps the AHJ registry updated.
                    Users submit edits on AHJ pages and AHJ officials will accept or reject edits depending on their accuracy."
                    pictureSide="right"
                    imgSrc="/images/AboutPage/ComponentPictures/ahj_edits.png"
                    ></feature-section>

    <!-- Account Description Section (describes what you can do with an account) -->
    <div id="account-description-section" v-if="!LoggedIn">
        <h2>Create an Account</h2>
        <div id="account-feature-list">
            <account-feature-description headerText="API Access" 
                    paragraphText="Gain throttled access to our API when you request an API token"
                    imgSrc="/images/AboutPage/CreateAccountIcons/lock.png"
                    ></account-feature-description>
            <account-feature-description headerText="Edit Access" 
                        paragraphText="Submit / accept edit requests to keep the registry up to date"
                        imgSrc="/images/AboutPage/CreateAccountIcons/colab.png"
                        ></account-feature-description>
            <account-feature-description headerText="Leaderboards" 
                        paragraphText="View nationwide leaderboards to see the registry's top contributors"
                        imgSrc="/images/AboutPage/CreateAccountIcons/leaderboard.png"
                        ></account-feature-description>
        </div>
        <b-button variant="primary" id="account-description-button" size="lg" @click="$router.push({ name: 'register' })">Create Account</b-button>
    </div>
  </div>
</template>

<script>
import FeatureSection from "../components/AboutPage/FeatureSection.vue";
import AccountFeatureDescription from "../components/AboutPage/AccountFeatureDescription.vue";
// Animate on scroll library (used mainly in FeatureSelection sections)
import AOS from 'aos';
import 'aos/dist/aos.css';

AOS.init();

export default {
    data() {
        return {
            Email: '',
            clientPhotos: ['titan_solar.png', 'aurora.jpg', 'solar_app.png', 'raise_green.png', 
            'ipsun_solar.jpg', 'solar_power_of_oklahoma.jpg', '17_terawatts.jpg', 'blue_banyan.jpg', 'sunspec_alliance.png'],
            clientPhotoLocation: "/images/AboutPage/clients/",
        }
    },
    computed: {
        LoggedIn(){
            return this.$store.getters.loggedIn;
        }
    },
    components: {
    "feature-section": FeatureSection,
    "account-feature-description": AccountFeatureDescription
  },
}
</script>

<style scoped>

h1 {
    font-size: 4.2rem;
}

h2 {
    font-size: 4rem;
}

h4 {
    font-size: 1.4rem;
}

h5 {
    font-size: 1.2rem;
}

.landing-page-container {
    padding-bottom: 4em;
}

#client-section {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
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
    margin-top: 2em;
    width: 100%;
}

#about-section > * {
    text-align: center;
    width: 70%;
    margin: 30px auto 20px;
}

.about-section-description {
    text-align: left !important;
}

#about-section-header {
    margin: 1em auto 0.8em;
}


#videowrapper {
  position: relative;
  width: 100%;
  padding-top: 56.25%; /* 16:9 Aspect Ratio (divide 9 by 16 = 0.5625) */
  height: 0;
}

#videowrapper iframe {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
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

@media (min-width: 2200px){
    #videowrapper {
        width: 80%;
        margin: 0 auto;
    }
    h4 {
        font-size: 2.2rem;
    }

    h5 {
        font-size: 1.8rem;
    }
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
    h5 {
        font-size: 1rem;
    }
    #about-section > * {
        margin: 30px auto 10px;
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
        font-size: 1.1rem;
    }
    #client-section > *{
        max-height: 100px;
        max-width: 130px;
        margin-top: 5px;
    }
    #about-section h4 {
        width: 80%;
    }
    .about-section-description-extended {
        display: none;
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
