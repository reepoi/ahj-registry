<template>
  <div id="adobe-dc-view">
  </div>
</template>

<script>

export default {
 name: "Editor",
 data() {
   return{
     pdfEditor: null
   }
 },
 methods: {
   /*
    * Initialize the editor
    */
   setup() {
        // to use this loading, type into command line: npm install --save vue-plugin-load-script
        this.$loadScript("https://documentcloud.adobe.com/view-sdk/main.js")
        .then(() => {
          this.listenForFileUpload();
        })
        .catch(() => {
          // Failed to fetch script
        });
   },
   /* Helper function to listen for file upload and
    * creating Promise which resolve to ArrayBuffer of file data.
    **/
  listenForFileUpload() {
    var fileToRead = document.getElementById("file-picker");
    var that = this;
    fileToRead.addEventListener("change", function () {
        var files = fileToRead.files;
        if (files.length > 0 && that.isValidPDF(files[0])) {
            var fileName = files[0].name;
            var reader = new FileReader();
            reader.onloadend = function (e) {
                var filePromise = Promise.resolve(e.target.result);
                that.previewFile(filePromise, fileName);
            };
            reader.readAsArrayBuffer(files[0]);
        }
    }, false);
},
  isValidPDF(file) {
    if (file.type === "application/pdf") {
        return true;
    }
    if (file.type === "" && file.name) {
        var fileName = file.name;
        var lastDotIndex = fileName.lastIndexOf(".");
        return !(lastDotIndex === -1 || fileName.substr(lastDotIndex).toUpperCase() !== "PDF");
    }
    return false;
  },
  previewFile(filePromise, fileName) {
    /* Initialize the AdobeDC View object */
    var adobeDCView = new window.AdobeDC.View({
        /* Pass your registered client id */
        clientId: "9e846a119d9048b6a826f9721ddbae5e",
        /* Pass the div id in which PDF should be rendered */
        divId: "adobe-dc-view",
    });

    /* Invoke the file preview API on Adobe DC View object */
    adobeDCView.previewFile({
        /* Pass information on how to access the file */
        content: {
            /* pass file promise which resolve to arrayBuffer */
            promise: filePromise,
        },
        /* Pass meta data of file */
        metaData: {
            /* file name */
            fileName: fileName
        }
    }, {});
  }
 },
 /*
  * Load the editor when this component is mounted
  */
 mounted() {
   this.setup();
 }
};
</script>

<style>
</style>