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
    let get_host = function() { return window.location.href; }
    it.each([
        [{AHJName: 'name'}, `${get_host()}?AHJName=name`],
        [{BuildingCode: ['2021IBC', '2018IBC']}, `${get_host()}?BuildingCode=2021IBC,2018IBC`],
        [{AHJName: 'name', AHJCode: 'code'}, `${get_host()}?AHJName=name&AHJCode=code`],
        [{AHJName: 'name', BuildingCode: ['2021IBC', '2018IBC']}, `${get_host()}?AHJName=name&BuildingCode=2021IBC,2018IBC`]
    ])('Parameterized URL', (parameters, expected) => {
        expect.assertions(1);
        Object.keys(parameters).forEach(k => s.vm.parameters[k] = parameters[k]);
        let url = s.vm.getParameterizedURL();
        expect(url).toBe(expected);
        // reset filters for next tests (clearFilters is tested above)
        s.vm.clearFilters();
    });
    it('Parameterized URL GeoJSON', () => {
        expect.assertions(1);
        store.state.searchedGeoJSON = objects.geoJSONLocation;
        s.vm.parameters.AHJName = 'Madera';
        let url = s.vm.getParameterizedURL();
        let expected = `${get_host()}?AHJName=Madera&GeoJSON=%7B%22type%22%3A%22FeatureCollection%22%2C%22features%22%3A%5B%7B%22type%22%3A%22Feature%22%2C%22properties%22%3A%7B%7D%2C%22geometry%22%3A%7B%22type%22%3A%22Point%22%2C%22coordinates%22%3A%5B-119.088827%2C36.315125%5D%7D%7D%5D%7D`;
        expect(url).toBe(expected);
        // reset filters for next tests (clearFilters is tested above)
        s.vm.clearFilters();
        store.state.searchedGeoJSON = null;
    });
    it.each([
        [{AHJName: 'name'}, {AHJName: 'name'}],
        [{BuildingCode: '2021IBC,2018IBC'}, {BuildingCode: ['2021IBC', '2018IBC']}],
        [{AHJName: 'name', AHJCode: 'code'}, {AHJName: 'name', AHJCode: 'code'}],
        [{AHJName: 'name', BuildingCode: '2021IBC,2018IBC'}, {AHJName: 'name', BuildingCode: ['2021IBC', '2018IBC']}]
    ])('Read Parameterized URL Query', (vueQueryObject, expected_values) => {
        s.vm.setQueryFromObject(vueQueryObject);
        Object.keys(expected_values).forEach(k => expect(s.vm.parameters[k]).toEqual(expected_values[k]));
        s.vm.clearFilters();
    });
    it('Read Parameterized URL Query GeoJSON', () => {
        expect.assertions(2);
        let vueQueryObject = {AHJName: 'Madera', GeoJSON: '%7B%22type%22%3A%22FeatureCollection%22%2C%22features%22%3A%5B%7B%22type%22%3A%22Feature%22%2C%22properties%22%3A%7B%7D%2C%22geometry%22%3A%7B%22type%22%3A%22Point%22%2C%22coordinates%22%3A%5B-119.088827%2C36.315125%5D%7D%7D%5D%7D'};
        s.vm.setQueryFromObject(vueQueryObject);
        expect(s.vm.parameters.AHJName).toBe(vueQueryObject.AHJName);
        expect(store.state.searchedGeoJSON).toEqual(objects.geoJSONLocation);
        // reset filters for next tests (clearFilters is tested above)
        s.vm.clearFilters();
        store.state.searchedGeoJSON = null;
    });
});