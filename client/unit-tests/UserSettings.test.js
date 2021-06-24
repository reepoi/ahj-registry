/**
 * @jest-environment jsdom
 */

import { mount } from '@vue/test-utils';
import UserSettings from '../src/views/UserAccounts/UserSettings';
import { createLocalVue } from '@vue/test-utils';
import { BootstrapVue, BootstrapVueIcons } from "bootstrap-vue";
import store from '../src/store.js';
import * as objects from './test_objs'; 

const localVue = createLocalVue();
localVue.use(BootstrapVue);
localVue.use(BootstrapVueIcons);
var u;
const div = document.createElement('div');
document.body.appendChild(div)

beforeAll(async () => {
    u = await mount(UserSettings, { localVue, store, mocks: { $route: { query: "" }}, attachTo: div });
}); 

describe('Mount tests', () => {
    it('Component mounts', () => {
        expect(u.vm.selectedComponent).toEqual('EditProfile');
    });
});

describe('Method tests', () => {
    it('Change selected components', () => {
        u.vm.ChangeSelectedComponent('API');
        expect(u.vm.selectedComponent).toEqual('API');
        u.vm.ChangeSelectedComponent('API');
        expect(u.vm.selectedComponent).toEqual('API');
    });
});