<template>
  <div>
  </div>
</template>

<script>
import axios from "axios";
import constants from "../../../constants.js";

export default {
  // When logout is called, try to send a logout request to the backend. Regardless of whether the logout was successful on the backend,
  // we want to log out the user on the front-end. So we change the store's auth token, reset currentUserInfo, and navigate to the search page.
  created() {
    axios.post(constants.API_ENDPOINT + "auth/token/logout/", {},{
      headers: {
        Authorization: this.$store.getters.authToken,
      }
    }).then(() => {
      this.$store.commit("changeAuthToken", "");
      this.$store.commit("changeCurrentUserInfo", null);
      this.$router.push({name: 'ahj-search'});
    }).catch(() => {
      this.$store.commit("changeAuthToken", "");
      this.$store.commit("changeCurrentUserInfo", null);
      this.$router.push({name: 'ahj-search'});
    });
  }
}
</script>