<template>
  <b-navbar toggleable="lg">
    <router-link :to="{ name: 'ahj-search' }">
      <b-navbar-brand>
        <img id="oblogo" src="@/assets/ob.png" />
        <h1 class="app-title">AHJ Registry</h1>
      </b-navbar-brand>
    </router-link>

    <b-navbar-toggle target="nav-collapse"></b-navbar-toggle>

    <b-collapse id="nav-collapse" is-nav>
      <b-navbar-nav class="mr-auto navbar-background">
        <b-nav-item href="#/about">About</b-nav-item>
        <b-nav-item href="#/ahj-search">Search</b-nav-item>
        <!-- <b-nav-item href="#/ahj-search">API</b-nav-item> -->
        <b-nav-item href="#/data-vis">Data Analytics</b-nav-item>
        <!-- <b-nav-item href="#/ahj-pdf-markup" v-if="loggedIn">PDF Editor</b-nav-item> -->
        <!-- <b-nav-item href="#/leaderboard" v-if="loggedIn">Leaderboard</b-nav-item> -->
      </b-navbar-nav>
      <b-navbar-nav class="ml-auto navbar-background">
        <b-nav-item href="#/login" v-if="!loggedIn">Login</b-nav-item>
        <b-nav-item href="#/register" v-if="!loggedIn">Register</b-nav-item>
        <b-nav-item-dropdown right v-if="loggedIn">
            <template #button-content>
              <img v-if="Photo !== null" class="user-photo" :src="Photo">
              <img v-else class="user-photo" src="../assets/images/profile-image-default.jpeg">
            </template>
            <b-dropdown-item :href="'#/user/' + Username"> 
              <b-icon icon="person"></b-icon>
              Profile
            </b-dropdown-item>
            <b-dropdown-item href="#/settings">
              <b-icon icon="gear"></b-icon>
              Account Settings
            </b-dropdown-item>
            <b-dropdown-item href="#/logout">
            <b-icon icon="box-arrow-right"></b-icon>
              Sign Out
            </b-dropdown-item>
        </b-nav-item-dropdown>
      </b-navbar-nav>
    </b-collapse>
  </b-navbar>
</template>

<script>
export default {
  computed: {
    loggedIn() {
      return this.$store.getters.loggedIn;
    },
    Photo() {
      return this.$store.state.loginStatus.Photo;
    },
    Username() {
      return this.$store.state.loginStatus.Username;
    }
  },
  watch: {
    "$store.state.loginStatus": function() {
    }
  }
}
</script>

<style scoped>
nav {
  font-family: "Segoe UI";
  font-size: 18px;
  font-style: normal;
  display: flex;
  padding-left: 20px;
  border-bottom: 1px solid #dadce0;
  padding-top: 12px;
}

.navbar-brand {
  margin-right: 30px;
}

#oblogo {
  margin-top: -8px;

  width: auto;
  height: 50px;
}

.nav-link {
  color: #3b3932 !important;
}

.app-title {
  font-family: "Roboto";
  font-size: 25px;
  font-weight: bold;
  display: inline;
  text-transform: uppercase;
  margin-left: 5px;
}

.user-photo {
  width: 3em;
  border-radius: 2em;
}

#nav-collapse {
  z-index: 1040;
}

@media (max-width: 990px){
    .navbar-background {
      background-color: rgba(255, 255, 255, 0.9);
  }
}

</style>
