 import { mount } from '@vue/test-utils';
import editObj from '../src/components/AHJPage/EditObject';
import { createLocalVue } from '@vue/test-utils';
import BootstrapVue from 'bootstrap-vue';
import store from '../src/store.js';
import * as objects from './test_objs';

const localVue = createLocalVue();
var e;

beforeAll(async () => {
    localVue.use(BootstrapVue);
    e = await mount(editObj, { mocks: { $parent: { ...objects.AHJ } }, store, localVue, propsData: { data: {...objects.Edit} } });
});

describe('Object Mounts', () => {
    it('Edit Object Mounts', () => {
        expect(e.vm.data.ReviewStatus).toEqual("A");
    })
});

describe('Method tests', () => {
    it('Change Status', () => {
        e.vm.data.ReviewStatus = "R";
        e.vm.changeStatus();
        expect(e.vm.$refs.eobj.style.backgroundColor).toEqual("rgb(255, 190, 190)");
    });
});