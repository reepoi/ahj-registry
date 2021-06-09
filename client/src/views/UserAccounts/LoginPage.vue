<template>
  <div class="login-page-container">
      <component-login></component-login>
  </div>
</template>

<script>
import Login from "../../components/UserAccounts/Login.vue";
export default {
  components: {
    "component-login": Login
  }
};
</script>

<style scoped>
.login-page-container {
  background-color: #f7f7f7;
  overflow: hidden;
}
</style>
