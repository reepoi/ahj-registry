<template>
  <div class="public-filter">
    <form @submit.prevent>
      <label for="file-picker">Choose a PDF File:</label>
      <input type="file" id="file-picker" name="file-picker" accept="application/pdf">
    </form>
  </div>
</template>

<script>
export default {
}
</script>

<style scoped>
</style>
