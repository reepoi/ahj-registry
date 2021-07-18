import 'expect-puppeteer';
import { executablePath } from 'puppeteer';
import * as settings from './test_settings.js';

jest.setTimeout(600000);

describe('Data vis tests', () => {
    beforeAll(async () => {
        await page.goto(settings.host + 'ahj-search');
        let loginButton = await page.$('a[href="#/login"]');
        await loginButton.click();
        let email = await page.$('input[placeholder="Email"]');
        await email.type(settings.email, { delay: 100 });
        let password = await page.$('input[placeholder="Password"]');
        await password.type(settings.password, { delay: 100 });
        loginButton = await page.$('#login-button');
        await loginButton.click();
        await page.waitForNavigation({ waitUntil: 'networkidle0' });
        await page.goto(settings.host + "data-vis/");
    });
    it('Page loads', async () => {
        await expect(page).toMatch("Explore where the AHJ Registry has permitting information");
    });
    it('Circles render eventually', async () => {
        let circle = await page.waitForSelector(".leaflet-marker-icon.marker-cluster.marker-cluster-large.leaflet-zoom-animated.leaflet-interactive");
        expect(circle).toBeTruthy();
    });
    it('Select new data', async () => {
        let radioButtn = await page.$('#map-radio-numWindCodes');
        await radioButtn.click();
        let circle = await page.waitForSelector(".leaflet-marker-icon.marker-cluster.marker-cluster-large.leaflet-zoom-animated.leaflet-interactive");
        expect(circle).toBeTruthy();
        await new Promise(r => setTimeout(r, 1000));
    });
});
