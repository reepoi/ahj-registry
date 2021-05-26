import 'expect-puppeteer';
import { executablePath } from 'puppeteer';

jest.setTimeout(30000);

describe('AHJ Page Tests', () => {
    beforeAll(async () => {
        await page.goto('http://localhost:8080/#/ahj-search');
        let xButton = await page.$(".introjs-skipbutton");
        await xButton.click();
    });
    it('Check page loads', async () => {
        await expect(page).toMatch('AHJ Registry');
    });
    it('Search in Searchbar', async () => {
        let el = await page.$('#search-bar-input');
        await el.type("353 S 1100 E", { delay: 100 });
        await el.press('Enter');
        let list = await page.$('.ahj-public-list');
        while(await page.$('.b-table-busy-slot')){}
        let tr = await list.$$('tr[tabindex="0"]');
        expect(tr.length).toBeGreaterThan(0);
    });
    it('Select an AHJ', async () => {
        let list = await page.$('.ahj-public-list');
        let tr = await list.$$('tr[tabindex="0"]');
        await tr[1].click();
        let b = await tr[1].$('button');
        await b.click();
        let r = await list.$$('.b-table-details');
        expect(r.length).toBe(1);
        await new Promise(r => setTimeout(r, 2000));
    });
    it('More search options', async () => {
        let b = await page.$('#showbutton');
        let a = await b.$('i');
        await a.click();
        await expect(page).toMatch('Building Codes');
        await expect(page).toMatch('More Search Options');
        await new Promise(r => setTimeout(r, 2000));
    });
    it('Building code dropdown', async () => {
        let bc = await page.$$('.options')
        bc = bc[0];
        let plus = await bc.$('#plusbutton');
        await plus.click();
        await expect(page).toMatchElement('#bcdrop', { visible: true });
        await expect(page).toMatchElement('#search-options-drop', { visible: false });
        await new Promise(r => setTimeout(r, 2000));
    });
    it('More search options dropdown', async () => {
        let bc = await page.$$('.options')
        bc = bc[1];
        let plus = await bc.$('#plusbuttonAHJ');
        await plus.click();
        await expect(page).toMatchElement('#search-options-drop', { visible: true });
        await expect(page).toMatchElement('#bcdrop', { visible: false });
        await new Promise(r => setTimeout(r, 2000));
    });
    it('Hover over leaflet marker', async () => {
        await page.hover(".awesome-marker-icon-blue");
        let mapdiv = await page.$("#mapdiv");
        await expect(mapdiv).toMatch("Salt Lake County");
        await new Promise(r => setTimeout(r, 2000));
    });
    it('Click marker', async () => {
        let markers = await page.$$(".awesome-marker-icon-lightblue");
        await markers[0].click();
        await markers[0].hover();
        await expect(page).toMatchElement('tr[aria-selected=true]');
        let mapdiv = await page.$("#mapdiv");
        await expect(mapdiv).toMatch("Salt Lake City");
        await new Promise(r => setTimeout(r, 2000));
    });
    it('Clear search', async () => {
        let [b] = await page.$x('//button[contains(.,"Clear")]');
        await b.click();
        await expect(page).not.toMatch('353 S 1100 E');
        await new Promise(r => setTimeout(r, 2000));
    });
});
