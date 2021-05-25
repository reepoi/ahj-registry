import { mount } from '@vue/test-utils';
import AHJTableView from '../src/components/SearchPage/AHJTableView';
import { createLocalVue } from '@vue/test-utils';
import { BootstrapVue, BootstrapVueIcons } from "bootstrap-vue";
import store from '../src/store.js';
import * as objects from './test_objs'; 

const localVue = createLocalVue();
localVue.use(BootstrapVue);
localVue.use(BootstrapVueIcons);
var p;


beforeAll(async () => {
    p = await mount(AHJTableView, { localVue, store, mocks: { $route: { query: "" }} });
});

describe('Mount tests', () => {
    it('Components mounts', () => {
        expect(p.vm.fields).toBeTruthy();
    });
});

describe('Method tests', () => {
    it('AHJ Code Formatter', () => {
        expect(p.vm.ahjCodeFormatter("2021IBC")).toEqual("2021 IBC");
        expect(p.vm.ahjCodeFormatter("NoSolarRegulations")).toEqual("No Solar Regulations");
    });
    it('Row get ahj address', () => {
        expect(p.vm.rowGetAHJAddress({ item: objects.AHJ })).toBe("353 S 1100 E Unit 12 <br>Salt Lake City Salt Lake County, UT 84102");
    });
});
