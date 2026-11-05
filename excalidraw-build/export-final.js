const puppeteer = require('puppeteer');
const fs = require('fs');

const inputFile = 'C:/ForumProject/docs/images/tremor_monitor_schematic_v2.excalidraw';
const outputFile = 'C:/ForumProject/docs/images/tremor_monitor_schematic_v2.png';

async function main() {
  const excalidrawData = fs.readFileSync(inputFile, 'utf8');
  
  const browser = await puppeteer.launch({
    headless: true,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-gpu',
      '--single-process',
      '--no-zygote',
      '--incognito',
      '--disable-web-security',
      '--allow-file-access-from-files'
    ]
  });
  
  const page = await browser.newPage();
  await page.setViewport({ width: 1400, height: 900, deviceScaleFactor: 2 });
  
  // Navigate to Excalidraw
  console.log('Navigating to excalidraw.com...');
  await page.goto('https://excalidraw.com/', { waitUntil: 'load', timeout: 60000 });
  
  console.log('Waiting for app to load...');
  // Wait for the canvas and app to be ready
  await page.waitForSelector('canvas', { timeout: 30000 });
  await page.waitForTimeout(5000);
  
  console.log('Loading diagram data...');
  // Inject the diagram via localStorage and reload
  await page.evaluate((data) => {
    localStorage.setItem('excalidraw', data);
    // Also set a flag to reload on next tick
    window.__needsReload = true;
  }, excalidrawData);
  
  // Reload to pick up the localStorage
  await page.reload({ waitUntil: 'load', timeout: 60000 });
  await page.waitForSelector('canvas', { timeout: 30000 });
  await page.waitForTimeout(5000);
  
  // Verify the diagram loaded
  const title = await page.title();
  console.log('Page title:', title);
  
  // Check for elements on canvas
  const elementCount = await page.evaluate(() => {
    return document.querySelectorAll('canvas').length;
  });
  console.log('Canvas count:', elementCount);
  
  // Take screenshot
  console.log('Taking screenshot...');
  await page.screenshot({ 
    path: outputFile, 
    fullPage: false,
    type: 'png'
  });
  
  const fileSize = fs.statSync(outputFile).size;
  console.log('PNG exported: ' + outputFile);
  console.log('File size: ' + fileSize + ' bytes');
  
  await browser.close();
  
  if (fileSize < 1000) {
    console.error('Warning: File size is very small, diagram may not have rendered');
    process.exit(1);
  }
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
