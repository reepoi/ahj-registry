<template>
    <div>
        <h1>Account Privileges</h1>
        <h4 id="ahj-jurisdiction-text">AHJs where your account can accept/reject edit requests:</h4>
        <template v-if="MaintainedAHJs.length === 0">
            <p>None.</p>
        </template>
        <template v-else>
            <ul>
                <li v-for="ahjName in MaintainedAHJs" :key="ahjName">{{ahjName}}</li>
            </ul>
        </template>
        <h5 id="help-text">If your email's domain matches the email/URL domain associated with an AHJ, then in the future you should automatically gain edit access for that AHJ.
            For now, please contact ahjregistry@sunspec.org if you do not have permission to edit your AHJ.
        </h5>
        <!-- <p>Note: If you still don't have edit access to your AHJ, contact Sunspec support at ahjregistry@sunspec.org</p> -->

    </div>
</template>

<script>
import axios from "axios";
import constants from "../../../constants.js";
export default {
    data() {
        return {
            ahjNames: []
        }
    },
    computed: {
        MaintainedAHJs(){
            return this.ahjNames;
        }
    },
    methods: {
        GetAHJNames(MaintainedAHJs){
            for (let PKIndex in MaintainedAHJs){
                let query = constants.API_ENDPOINT + "ahj-one/";
                axios.get(query,
                    {
                    params: {
                        'AHJPK': MaintainedAHJs[PKIndex]
                    }
                    })
                    .then( (response) => {
                        this.ahjNames.push(response.data[0].AHJName.Value);
                    })
                    .catch(() => {
                    });
            }
        }
    },
    mounted() {
        this.GetAHJNames(this.$store.state.loginStatus.MaintainedAHJs);
    }
}
</script>

<style scoped>
#help-text {
    margin-top: 50px;
}
@media (max-width: 650px){
    h1 {
        font-size: 2rem;
        margin-bottom: 1em;
    }
    #help-text {
        font-size: 1rem;
    }
    #ahj-jurisdiction-text {
        font-size: 1.3rem;
    }
}
</style>