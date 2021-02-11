import Vue from "vue";
import App from "./App.vue";
import router from "./router";
import store from "./store";

import BootstrapVue from "bootstrap-vue";
import AwesomeMarkers from 'drmonty-leaflet-awesome-markers';

import "bootstrap/dist/css/bootstrap.css";
import "bootstrap-vue/dist/bootstrap-vue.css";

import "vue-awesome/icons";
import Icon from "vue-awesome/components/Icon";

require("./assets/MarkerStyles/leaflet.awesome-markers.css");
require("./assets/MarkerStyles/leaflet.awesome-markers.js");

Vue.component("v-icon", Icon);

Vue.use(BootstrapVue);
Vue.use(AwesomeMarkers);
Vue.config.productionTip = false;

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount("#app");
