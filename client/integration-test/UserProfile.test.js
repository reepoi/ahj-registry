import 'expect-puppeteer';
import { executablePath } from 'puppeteer';
import * as settings from './test_settings.js';

jest.setTimeout(60000);

describe('User Profile tests', () => {
    beforeAll(async () => {
        await page.goto(settings.host + 'ahj-search');
        let xButton = await page.$(".introjs-skipbutton");
        await xButton.click();
        let loginButton = await page.$('a[href="#/login"]');
        await loginButton.click();
    });
    it('Login', async () => {
        let email = await page.$('input[placeholder="Email"]');
        await email.type(settings.email, { delay: 100 });
        let password = await page.$('input[placeholder="Password"]');
        await password.type(settings.password, { delay: 100 });
        let loginButton = await page.$('#login-button');
        await loginButton.click();
        await page.waitForNavigation({ waitUntil: 'networkidle0' });
        let xButton = await page.$(".introjs-skipbutton");
        await xButton.click();
        expect(true).toBeTruthy();
        await new Promise(r => setTimeout(r, 5000));
    });
    it('Navigate to User Profile', async () => {
        let dropD = await page.$('a[href="#"]');
        await dropD.click();
        let profileButton = await page.$('a[href^="#/user/"]');
        await profileButton.click();
        await new Promise(r => setTimeout(r, 2000));
    });
    it('User contact info', async () => {
        let contactInfo = await page.$('button.contact-info-button');
        await contactInfo.click();
        await expect(page).toMatchElement('div.modal-content', { visible: true });
        let exit = await page.$('button.btn-primary');
        await exit.click();
        await expect(page).not.toMatchElement('div.modal-content', { visible: true });
    });
    it('Edit profile button', async () => {
        await new Promise(r => setTimeout(r, 1000));
        let [editButton] = await page.$x('//button[contains(.,"Edit Profile")]');
        await editButton.click();
        while( await page.waitForXPath('//*[contains(text(), "Loading")]', { hidden: true }) !== null){}
        await expect(page).toMatch('Update profile picture');
    });
    it('Navigate to API', async () => {
        let apiButton = await page.$('#api-button');
        await apiButton.click();
        while( await page.waitForXPath('//*[contains(text(), "Loading")]', { hidden: true }) !== null){}
        await expect(page).toMatch("Generate New Token");
        await new Promise(r => setTimeout(r, 1000));
    });
    it('Generate new token', async () => {
        let tokenButton = await page.$('#generate-token-button');
        await tokenButton.click();
        while( await page.waitForXPath('//*[contains(text(), "Generating Token")]', { hidden: true }) !== null){}
        await expect(page).toMatch('Your new API token');
        await new Promise(r => setTimeout(r, 2000));
    });
});
