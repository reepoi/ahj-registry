/**
 * @jest-environment jsdom
 */

import { mount } from '@vue/test-utils';
import UserProfile from '../src/views/UserAccounts/UserProfile';
import { createLocalVue } from '@vue/test-utils';
import { BootstrapVue, BootstrapVueIcons } from "bootstrap-vue";
import store from '../src/store.js';
import * as objects from './test_objs'; 

const localVue = createLocalVue();
localVue.use(BootstrapVue);
localVue.use(BootstrapVueIcons);
var u;


beforeAll(async () => {
    u = await mount(UserProfile, { localVue, store, mocks: { $route: { query: "" }} });
});

describe('Mount tests', () => {
    it('Component mounts', () => {
        expect(u.vm.goldBadgeCount).toBe(0);
    });
});

describe('Method tests', () => {
    it('Get User Profile', () => {
        u.vm.GetUserActivity('Edit');
        expect(u.vm.FeedActivity).toEqual('Edit');
    });
    it('Get badge', () => {
        let badge = u.vm.getBadge('badge',400,[300,401]);
        expect(badge).toEqual('images/Badges/badge/silver.png');
        badge = u.vm.getBadge('badge',402,[300,401]);
        expect(badge).toEqual('images/Badges/badge/gold.png');
        badge = u.vm.getBadge('badge',299,[300,401]);
        expect(badge).toEqual('images/Badges/badge/bronze.png');
    });
    it('Get badges', () => {
        u.vm.ProfileData = { 
            APICalls: 29,
            CommunityScore: 500,
            AcceptedEdits: 23
        };
        u.vm.getBadges();
        expect(u.vm.apiUsageBadge).toEqual("images/Badges/api-usage/bronze.png");
        expect(u.vm.communityScoreBadge).toEqual("images/Badges/community-score/gold.png");
        expect(u.vm.acceptedEditsBadge).toEqual("images/Badges/edits-accepted/gold.png");
    });
});