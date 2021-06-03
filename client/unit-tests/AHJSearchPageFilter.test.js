/**
 * @jest-environment jsdom
 */

import { mount } from '@vue/test-utils';
import AHJSearchPageFilter from '../src/components/SearchPage/AHJSearchPageFilter';
import { createLocalVue } from '@vue/test-utils';
import { BootstrapVue, BootstrapVueIcons } from "bootstrap-vue";
import store from '../src/store.js';
import * as objects from './test_objs'; 

const localVue = createLocalVue();
localVue.use(BootstrapVue);
localVue.use(BootstrapVueIcons);
var s;


beforeAll(async () => {
    s = await mount(AHJSearchPageFilter, { localVue, store, mocks: { $route: { query: "" }} });
});

describe('Mount tests', () => {
    it('Search page mounts', () => {
        expect(s.vm.filterToggled).toBe(true);
    });
    it('Mounts with query parameter', async () => {
        let s2 = await mount(AHJSearchPageFilter, { localVue, store, mocks: { $route: { query: { FireCode: "2021IFC,2018IFC" }} } });
        expect(s2.vm.parameters.FireCode).toEqual(["2021IFC","2018IFC"]);
    });
});

describe('Method tests', () => {
    it("Toggle search filter", () => {
        s.vm.SearchFilterToggled();
        expect(s.vm.filterToggled).toBe(false);
    });
    it("Clear filters", () => {
        var currFilter = {...s.vm.parameters };
        s.vm.parameters.BuildingCode = ['2021IBC'];
        s.vm.clearFilters();
        expect(s.vm.parameters).toEqual(currFilter);
    });
    it("Parameterized URL", () => {
        s.vm.parameters.BuildingCode = ['2021IBC','2018IBC'];
        var url = s.vm.getParameterizedURL();
        expect(url).toEqual("http://localhost/?view=latest&BuildingCode=2021IBC,2018IBC");
    });
});