import { mount } from '@vue/test-utils'
import AHJPage from './src/views/AHJPage.vue'
import { createLocalVue } from '@vue/test-utils';
import BootstrapVue from 'bootstrap-vue';
import VueRouter from 'vue-router';
import store from './src/store.js';

const localVue = createLocalVue();
localVue.use(BootstrapVue);
const p = mount(AHJPage, {mocks: { $route : { params: { AHJID: 1338 } } },store, localVue});


describe('AHJPage tests', () => {
  it('AHJPage mounts', async function() {
    expect(p.vm.$route.params.AHJID).toBe(1338);
  });
});

