import { mount } from '@vue/test-utils';
import AHJTablePagination from '../src/components/SearchPage/AHJTablePagination';
import { createLocalVue } from '@vue/test-utils';
import { BootstrapVue, BootstrapVueIcons } from "bootstrap-vue";
import store from '../src/store.js';
import * as objects from './test_objs'; 

const localVue = createLocalVue();
localVue.use(BootstrapVue);
localVue.use(BootstrapVueIcons);
var p;


beforeAll(async () => {
    p = await mount(AHJTablePagination, { localVue, store, mocks: { $route: { query: "" }} });
});

describe('Mount tests', () => {
    it('Pagination mounts', () => {
        expect(p.vm.perPage).toBe(20);
    });
});

describe('Method tests', () => {
    it('Set pagination',() => {
        p.vm.setPagination(20);
        expect(p.vm.pages.length).toBe(1);
    });
    it('Reset Pagination', () => {
        p.vm.pages = [1,2,3,4,5,6,7];
        p.vm.resetPagination();
        expect(p.vm.pages).toEqual([]);
    });
    it('Call for page', () => {
        store.state.searchedQuery = {}
        p.vm.currentPage = 1;
        p.vm.pages = [1,2,3,4,5,6,7];
        p.vm.callForPage(6);
        expect(p.vm.currentPage).toBe(6);
    });
});