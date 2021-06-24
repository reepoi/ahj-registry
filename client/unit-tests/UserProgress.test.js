/**
 * @jest-environment jsdom
 */

import { mount } from '@vue/test-utils';
import UserProgress from '../src/views/UserAccounts/UserProgress';
import { createLocalVue } from '@vue/test-utils';
import { BootstrapVue, BootstrapVueIcons } from "bootstrap-vue";
import store from '../src/store.js';
import * as objects from './test_objs'; 

const localVue = createLocalVue();
localVue.use(BootstrapVue);
localVue.use(BootstrapVueIcons);
var u;


beforeAll(async () => {
    u = await mount(UserProgress, { localVue, store, mocks: { $route: { query: "" }} });
});

describe('Mount tests', () => {
    it('Component mounts', () => {
        expect(u.vm.profileInfoLoaded).toBe(false);
    });
});

describe('Method tests', () => {
    it('Get badge data', () => {
        let badgeData = u.vm.getBadgeData('badge', 400, [0,300,401]);
        expect(badgeData).toEqual({
               "currBadge": "images/Badges/badge/gold.png",
               "max": 401,
               "nextBadge": "images/Badges/badge/gold-dark.png",
               "score": 400,
            });
    });
});