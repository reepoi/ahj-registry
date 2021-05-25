import { mount } from '@vue/test-utils';
import Contact from '../src/components/AHJPage/ContactCard';
import { createLocalVue } from '@vue/test-utils';
import BootstrapVue from 'bootstrap-vue';
import store from '../src/store.js';
import * as objects from './test_objs';

const localVue = createLocalVue();
var c;

beforeAll(async () => {
    localVue.use(BootstrapVue);
    c = await mount(Contact, { mocks: { $parent: { ...objects.AHJ } }, store, localVue, propsData: { data: {...objects.Contact}, eID: 2  } });
});

describe('Mount Tests', () => {
    it('FeeStructure Mounts', () => {
        expect(c.vm.editStatus).toEqual('A');
    })
});

describe('Method Tests', () => {
    it('Change Status', async () => {
        await c.setProps({ data: {...objects.Contact}, eID: 2, editStatus: "R"  })
        c.vm.changeStatus();
        expect(c.vm.$refs.cc.style.backgroundColor).toEqual("red");
    });
    it('Clear Edits', () => {
        c.vm.Edits.Title = "New title";
        c.vm.clearEdits();
        expect(c.vm.Edits.Title).not.toEqual("New Name");
    });
    it('Format Address', () => {
        let testAddress = { 
            AddressID: { Value: 2 },
            AddrLine1: { Value: "309 Field Crest PKWY" },
            AddrLine2: { Value: "" },
            AddrLine3: { Value: "Third Thing"},
            City: { Value: "" },
            County: { Value: "" },
            StateProvince: { Value: "LA" },
            Country: { Value: "" },
            ZipPostalCode: { Value: "84102" },
            Description: { Value: "Address Description" },
            AddressType: { Value:  "Mailing" },
            Location: null
          };
          c.vm.formatAddress(testAddress);
          expect(c.vm.AddressString).toBe("309 Field Crest PKWY, Third Thing, LA, 84102");
    });
});