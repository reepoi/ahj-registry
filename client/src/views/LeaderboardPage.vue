<template>
  <div class="leaderboard-page-container">
    <div class="leaderboard-component">
      <component-leaderboard></component-leaderboard>
    </div>
  </div>
</template>

<script>
import Leaderboard from "../components/Leaderboard.vue";
export default {
  components: {
    "component-leaderboard": Leaderboard
  }
};
</script>

<style scoped>
.leaderboard-page-container {
  display: grid;
  grid-template-columns: 20% auto 20%;
  grid-template-rows: 10% auto;
  overflow:scroll;
}

.leaderboard-component {
  grid-column: 2;
  grid-row: 2;
}
</style>
