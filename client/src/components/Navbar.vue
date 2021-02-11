<template>
  <nav class="navbar navbar-expand-sm navbar-light navbar-custom">
    <router-link to="ahj-search" class="navbar-brand">
      <img id="oblogo" src="@/assets/ob.png" />
      <h1 class="app-title">AHJ Registry</h1>
    </router-link>
    <ul class="navbar-nav ml-auto">
      <li class="nav-item">
        <router-link :to="{ name: 'ahj-search' }" class="nav-link">Search</router-link>
      </li>
      <li class="nav-item">
        <router-link :to="{ name: 'history' }" class="nav-link">History</router-link>
      </li>
      <li v-if="!isLogin" class="nav-item">
        <button class="nav-link" @click="$store.commit('setShowLoginModal', true)">Login</button>
      </li>
      <li v-if="isLogin" class="nav-item">
        <button class="nav-link" @click="logout()">Logout</button>
      </li>
    </ul>
  </nav>
</template>

<script>
export default {
  computed: {
    isLogin() {
      return this.$store.state.loginStatus["status"] === "success";
    },
    isSuper() {
      return this.$store.state.loginStatus["isSuper"];
    }
  },
  methods: {
    logout() {
      this.$store.commit("changeUserLoginStatus", {
            status: "",
            isSuper: false,
            isStaff: false,
            authToken: ""
      });
    }
  }
}
</script>

<style scoped>
.navbar-custom .navbar-brand:hover {
  color: #3b3932;
}
nav {
  font-family: "Roboto Condensed";
  font-size: 18px;
  font-style: normal;
  display: grid;
  grid-template-columns: 600px 1fr;
  padding-left: 20px;
  border-bottom: 1px solid #dadce0;
  padding-top: 12px;
}

.navbar-custom {
  background-color: white;
}

.navbar-custom .navbar-brand {
  color: #3b3932;
}

#oblogo {
  margin-top: -8px;

  width: auto;
  height: 50px;
}

.nav-link {
  color: #3b3932 !important;
  background:none;
  border:none;
  padding-top: 0px;
  outline: none;
}

.app-title {
  font-family: "Roboto";
  font-size: 25px;
  font-weight: bold;
  display: inline;
  text-transform: uppercase;
  margin-left: 5px;
}
</style>


