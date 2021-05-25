import { mount } from '@vue/test-utils';
import FeeStructure from '../src/components/AHJPage/FeeStructure';
import { createLocalVue } from '@vue/test-utils';
import BootstrapVue from 'bootstrap-vue';
import store from '../src/store.js';
import * as objects from './test_objs';

const localVue = createLocalVue();
var f;

beforeAll(async () => {
    localVue.use(BootstrapVue);
    f = await mount(FeeStructure, { mocks: { $parent: { ...objects.AHJ } }, store, localVue, propsData: { data: {...objects.FS}, eID: 2  } });
});

describe('Mount Tests', () => {
    it('FeeStructure Mounts', () => {
        expect(f.vm.editStatus).toEqual('A');
    })
});

describe('Method Tests', () => {
    it('Change Status', async () => {
        await f.setProps({ data: {...objects.FS}, eID: 2, editStatus: "R"  })
        f.vm.changeStatus();
        expect(f.vm.$refs.fs.style.backgroundColor).toEqual("red");
    });
    it('Clear Edits', () => {
        f.vm.Edits.FeeStructureName = "New Name";
        f.vm.clearEdits();
        expect(f.vm.Edits.FeeStructureName).not.toEqual("New Name");
    });
});
