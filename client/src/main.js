/*
 * The entry point for running the webpage
 */
import Vue from "vue";
import App from "./App.vue";
import store from "./store";
import router from "./router";
import Vuelidate from 'vuelidate'

import { BootstrapVue, BootstrapVueIcons } from "bootstrap-vue";
import AwesomeMarkers from "drmonty-leaflet-awesome-markers";

import "bootstrap/dist/css/bootstrap.css";
import "bootstrap-vue/dist/bootstrap-vue.css";
import LoadScript from 'vue-plugin-load-script';

require("./assets/MarkerStyles/leaflet.awesome-markers.css");
require("./assets/MarkerStyles/leaflet.awesome-markers.js");

require("./assets/MarkerStyles/MarkerCluster.css");
require("./assets/MarkerStyles/MarkerCluster.Default.css");

Vue.use(BootstrapVue);
Vue.use(Vuelidate);
Vue.use(BootstrapVueIcons);
Vue.use(AwesomeMarkers);
Vue.use(LoadScript);

Vue.loadScript("https://documentcloud.adobe.com/view-sdk/main.js");

// Initialize Vue app
new Vue({
  router,
  store,
  render: h => h(App)
}).$mount("#app");
