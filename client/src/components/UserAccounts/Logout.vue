<template>
    <div>
    </div>
</template>

<script>
import axios from "axios";
import constants from "../../constants.js";

export default {
    created() {
        axios.post(constants.API_ENDPOINT + "auth/token/logout/", {},{
                headers: {
                Authorization: `${this.$store.state.loginStatus.authToken}`,
                }
            }).then(() => {
                localStorage.removeItem('loginStatus');
                localStorage.removeItem('vuex');
                this.$store.commit("changeUserLoginStatus", {
                            Username: "",
                            MaintainedAHJs: [],
                            Photo: "",
                            authToken: ""
                        });
                this.$router.push({name: 'ahj-search'})
            }).catch(() => {
                this.$router.push({name: 'ahj-search'})
                this.$store.commit("changeUserLoginStatus", {
                            Username: "",
                            MaintainedAHJs: [],
                            Photo: "",
                            authToken: ""
                        });
            });
    }
}
</script>