/**
 * @jest-environment jsdom
 */

import { mount } from '@vue/test-utils';
import DataVisMap from '../src/components/DataVisMap';
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
    d = await mount(DataVisMap, { localVue, store, mocks: { $route: { query: "" }}, attachTo: div, propsData: { mapCategories: [
        'all',
        'numBuildingCodes',
        'numElectricCodes',
        'numResidentialCodes',
        'numFireCodes', 
        'numWindCodes'
      ], selectedMapCategory: 'all' } });
});

describe('Mount tests', () => {
    it('Component mounts', () => {
        expect(d.vm.stateMarkers).toEqual({});
    });
});

describe('Method tests', () => {
    it('Get code numbers average', () => {
        let point = { 
            all: 0, 
            numBuildingCodes: 90,
            numElectricCodes: 110,
            numResidentialCodes: 400,
            numFireCodes: 20,
            numWindCodes: 2
        }
        let ratio = d.vm.getCodeNumbersAvg(point);
        expect(ratio).toBe(622/5)
    });
    it('Get background marker color', () => {
        let values = [];
        let color = d.vm.getMarkerBackgroundColor(values);
        expect(color).toEqual("background-color: rgba(0,0,0,0.6)");
        values = [0.7,0.43,0.7985];
        color = d.vm.getMarkerBackgroundColor(values);
        expect(color).toEqual("background-color: rgba(0.7,0.43,0.7985,0.6)");
    });
});