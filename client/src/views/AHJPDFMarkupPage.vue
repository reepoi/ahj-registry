<template>
  <div class="pdf-markup-container">
    <div class="pdf-markup-editor">
      <component-pdf-markup-editor></component-pdf-markup-editor >
    </div>
    <div class="pdf-markup-sidebar">
      <component-pdf-markup-sidebar></component-pdf-markup-sidebar>
    </div>
  </div>
</template>

<script>
import PDFMarkupEditor from "../components/PDFMarkupEditor.vue";
import PDFMarkupSidebar from "../components/PDFMarkupSidebar.vue";
export default {
  components: {
    "component-pdf-markup-editor": PDFMarkupEditor,
    "component-pdf-markup-sidebar": PDFMarkupSidebar
  }
};
</script>

<style scoped>
.pdf-markup-container {
  margin-top: 20px;
  display: grid;
  grid-template-columns: 70% 30%;
  grid-template-rows: 100%;
}

.pdf-markup-editor {
  grid-column: 1 / 1;
  grid-row: 1 / 1;
}

.pdf-markup-sidebar {
  grid-column: 2 / 2;
  grid-row: 1 / 1;
}

.nav-link {
  display: inline;
  padding: 0;
  padding-right: 5px;
}
</style>