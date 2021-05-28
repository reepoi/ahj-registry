import 'expect-puppeteer';
import { executablePath } from 'puppeteer';
import * as settings from './test_settings.js';

jest.setTimeout(60000);

describe('Data vis tests', () => {
    beforeAll(async () => {
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
