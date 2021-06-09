<template>
  <div class="register-page-container">
      <component-register></component-register>
  </div>
</template>

<script>
import Register from "../../components/UserAccounts/Register.vue";
export default {
  components: {
    "component-register": Register
  }
};
</script>

<style scoped>
.register-page-container {
  background-color: #f7f7f7;
}
</style>
