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
                Authorization: `${this.$store.getters.authToken}`,
                }
            }).then(() => {
                localStorage.removeItem('loginStatus');
                localStorage.removeItem('vuex');
                this.$store.commit("changeUserLoginStatus", {
                            status: "",
                            isSuper: false,
                            isStaff: false,
                            authToken: ""
                        });
                this.$router.push({name: 'home'})
            }).catch(error => {console.log(error.message)});
    }
}
</script>