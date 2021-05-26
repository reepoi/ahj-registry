/**
 * @jest-environment jsdom
 */

import { mount } from '@vue/test-utils';
import Inspection from '../src/components/AHJPage/Inspection';
import { createLocalVue } from '@vue/test-utils';
import BootstrapVue from 'bootstrap-vue';
import store from '../src/store.js';
import * as objects from './test_objs';
import AHJPage from '../src/views/AHJPage.vue'

const localVue = createLocalVue();
var i;
var p;

beforeAll(async () => {
    localVue.use(BootstrapVue);
    i = await mount(Inspection, {store, localVue, propsData: { data: {...objects.Inspection}, eID: 2, AHJPK: 1  } , sync: false });
});

describe('Mount Tests', () => {
    it('FeeStructure Mounts', () => {
        expect(i.vm.editStatus).toEqual('A');
    })
});

describe('Method Tests', () => {
    it('Change Status', async () => {
        await i.setProps({ data: {...objects.Inspection}, eID: 2, editStatus: "R" , AHJPK: 1  })
        i.vm.changeStatus();
        expect(i.vm.$refs.insp.style.backgroundColor).toEqual("red");
    });
    it('Clear Edits', () => {
        i.vm.Edits.AHJInspectionName = "New Name";
        i.vm.clearEdits();
        expect(i.vm.Edits.AHJInspectionName).not.toEqual("New Name");
    });
    it('Add to contacts', () => {
        i.vm.addToContacts([{...objects.Contact}]);
        expect(i.vm.AddCont.Value[0]).toEqual(objects.Contact);
    });
    it('Get edit objects', () => {
        i.vm.$children[0].Edits.Title = "New Title";
        var es = i.vm.getEditObjects();
        expect(es[0].NewValue).toEqual("New Title");
    });
    it('Get deletions', () => {
        i.vm.$children[0].isDeleted = true;
        i.vm.getDeletions();
        expect(i.vm.Deleted.Value.length).toBe(1);
    });
});
