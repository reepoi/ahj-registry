import 'expect-puppeteer';
import { executablePath } from 'puppeteer';

jest.setTimeout(30000);

describe('AHJPage Puppeteer tests', () => {
    beforeAll(async () => {
        await page.goto('http://localhost:8080/#/view-ahj/2118');
    });
    it('Page loads',async () => {
        await new Promise(r => setTimeout(r, 2000));
        let name = await page.evaluate(() => document.querySelector("#name").innerText  );
        while(name === 'Loading'){
            name = await page.evaluate(() => document.querySelector("#name").innerText  );
        }
        
        await expect(page).toMatch('Woodlake city');
    });
    it('Building code dropdown', async () => {
        let chev = await page.$('#BCNotesChev');
        await chev.click();
        await expect(page).toMatchElement('#BCNotes', { visible: true });
    });
    it('Electric code dropdown', async () => {
        let chev = await page.$('#ECNotesChev');
        await chev.click();
        await expect(page).toMatchElement('#ECNotes',  { visible: true });
    });
    it('Fire code dropdown', async () => {
        let chev = await page.$('#FCNotesChev');
        await chev.click();
        await expect(page).toMatchElement('#FCNotes',  { visible: true });
    });
    it('Residential code dropdown', async () => {
        let chev = await page.$('#RCNotesChev');
        await chev.click();
        await expect(page).toMatchElement('#RCNotes',  { visible: true });
    });
    it('Wind code dropdown', async () => {
        let chev = await page.$('#WCNotesChev');
        await chev.click();
        await expect(page).toMatchElement('#WCNotes',  { visible: true });
        await new Promise(r => setTimeout(r, 2000));
    });
    it('Show edits',async () => {
        let [editButton] = await page.$x('//a[contains(.,"Show Edits")]');
        await editButton.click();
        await expect(page).toMatchElement("#mid-edits",{ visible: true });
        let editDiv = await page.$('#edits');
        let xButton = await editDiv.$('.fas.fa-times');
        await xButton.click();
        await new Promise(r => setTimeout(r, 2000));
    });
    it('Edit this AHJ Button', async () => {
        let [editButton] = await page.$x('//a[contains(.,"Edit This AHJ")]');
        await expect(page).not.toMatchElement('[id^=__BVID__]', {visible: true});
        await editButton.click();
        await expect(page).toMatch("Cancel");
        await expect(page).toMatch("Submit Edits");
        await expect(page).toMatchElement('[id^=__BVID__]', {visible: true});
        await expect(page).toMatchElement('.fa.fa-plus');
        await expect(page).toMatchElement('.fa.fa-minus');
    });
});
