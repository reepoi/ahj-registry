import 'expect-puppeteer';
import { executablePath } from 'puppeteer';
import * as settings from './test_settings.js';

jest.setTimeout(600000);

describe('AHJPage Puppeteer tests', () => {
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
        await page.goto(settings.host + 'view-ahj/2118');
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
        //await expect(page).not.toMatchElement('[id^=__BVID__]', {visible: true});
        await editButton.click();
        await expect(page).toMatch("Cancel");
        await expect(page).toMatch("Submit Edits");
        await expect(page).toMatchElement('[id^=__BVID__]', {visible: true});
        await expect(page).toMatchElement('.fa.fa-plus');
        await expect(page).toMatchElement('.fa.fa-minus');
    });
    it('Make an edit', async () => {
        //await page.select('select#BCSelector',"2021IBC");
        let selects = await page.$$('select.custom-select.custom-select-sm');
        await selects[14].select("2011NEC");
        let textDiv = await page.$('div#text');
        let submit = await textDiv.$('a');
        await submit.click();
        let edits = await page.$('div#confirm-edits');
        await new Promise(r => setTimeout(r, 1000));
        let editObjs = await edits.$$('i.fas.fa-minus');
        expect(editObjs.length).toBe(1);
    });
    it('Submit an edit', async () => {
        let edits = await page.$('div#confirm-edits');
        let submit = await edits.$('a[style="margin: 0px 10px 0px 0px; padding: 0px; text-decoration: underline;"]');
        await submit.click();
        await expect(page).toMatchElement('div#confirm-edits', { visible: false }); 
        await new Promise(r => setTimeout(r, 2000));
    });
});
