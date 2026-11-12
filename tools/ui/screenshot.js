// node tools/ui/screenshot.js /abs/ui/preview/mockup.html /abs/ui/preview
// Screenshots the mock-up: hud.png (Index window hidden) and index.png (window open).
const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const [page_path, out_dir] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
  for (const [hash, name] of [['#hud', 'hud.png'], ['', 'index.png']]) {
    await page.goto('file://' + page_path + hash);
    await page.waitForSelector('body[data-ready="1"]', { timeout: 15000 });
    await page.evaluate((h) => { location.hash = h; }, hash);
    await page.waitForTimeout(200);
    await page.locator('#screen').screenshot({ path: path.join(out_dir, name) });
    console.log('saved', name);
  }
  await browser.close();
})();
