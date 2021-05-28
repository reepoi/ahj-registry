/**
 * @jest-environment jsdom
 */

import { mount } from '@vue/test-utils';
import DataVis from '../src/views/DataVis';
import { createLocalVue } from '@vue/test-utils';
import { BootstrapVue, BootstrapVueIcons } from "bootstrap-vue";
import store from '../src/store.js';
import * as objects from './test_objs'; 

const localVue = createLocalVue();
localVue.use(BootstrapVue);
localVue.use(BootstrapVueIcons);
var d;
const div = document.createElement('div');
document.body.appendChild(div)

beforeAll(async () => {
    d = await mount(DataVis, { localVue, store, mocks: { $route: { query: "" }}, attachTo: div });
});

describe('Mount tests', () => {
    it('Component mounts', () => {
        expect(d.vm.mapCategory).toEqual('all');
    });
});