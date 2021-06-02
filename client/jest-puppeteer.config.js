 
module.exports = {
  launch: {
    dumpio: false,
    headless: false,
    product: 'chrome',
    timeout: 0,
    defaultViewport:{
      width: 1600,
      height: 800,
      isLandscape: true,
      isMobile: false
    },
    args: ["--window-size=1600,800", '--no-sandbox',
    '--disable-setuid-sandbox']
  },
  browserContext: 'incognito',
}
