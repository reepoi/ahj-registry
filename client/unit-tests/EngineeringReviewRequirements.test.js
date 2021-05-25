import { mount } from '@vue/test-utils';
import ERR from '../src/components/AHJPage/EngineeringReviewRequirements';
import { createLocalVue } from '@vue/test-utils';
import BootstrapVue from 'bootstrap-vue';
import store from '../src/store.js';
import * as objects from './test_objs';

const localVue = createLocalVue();
var err;

beforeAll(async () => {
    localVue.use(BootstrapVue);
    err = await mount(ERR, { mocks: { $parent: { ...objects.AHJ } }, store, localVue, propsData: { data: {...objects.ERR}, eID: 2  } });
});

describe('Mount Tests', () => {
    it('FeeStructure Mounts', () => {
        expect(err.vm.editStatus).toEqual('A');
    })
});

describe('Method Tests', () => {
    it('Change Status', async () => {
        await err.setProps({ data: {...objects.ERR}, eID: 2, editStatus: "R"  })
        err.vm.changeStatus();
        expect(err.vm.$refs.err.style.backgroundColor).toEqual("red");
    });
    it('Clear Edits', () => {
        err.vm.Edits.RequirementLevel = "New Name";
        err.vm.clearEdits();
        expect(err.vm.Edits.RequirementLevel).not.toEqual("New Name");
    });
});
