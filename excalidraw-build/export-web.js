const puppeteer = require('puppeteer');
const fs = require('fs');

const inputFile = 'C:/ForumProject/docs/images/tremor_monitor_schematic_v2.excalidraw';
const outputFile = 'C:/ForumProject/docs/images/tremor_monitor_schematic_v2.png';

async function main() {
  const excalidrawData = fs.readFileSync(inputFile, 'utf8');
  
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--disable-gpu']
  });
  
  const page = await browser.newPage();
  await page.setViewport({ width: 1400, height: 900, deviceScaleFactor: 2 });
  
  // Navigate to Excalidraw
  await page.goto('https://excalidraw.com', { waitUntil: 'networkidle0', timeout: 30000 });
  
  // Wait for the app to be ready
  await page.waitForTimeout(5000);
  
  // Inject the diagram data
  await page.evaluate((data) => {
    // Store the data in localStorage
    localStorage.setItem('excalidraw', data);
    
    // Reload the page to pick up the data
    window.location.reload();
  }, excalidrawData);
  
  // Wait for reload and render
  await page.waitForTimeout(8000);
  
  // Take screenshot
  await page.screenshot({ 
    path: outputFile, 
    fullPage: false,
    clip: { x: 0, y: 0, width: 1400, height: 900 }
  });
  
  console.log('PNG exported: ' + outputFile);
  console.log('Size: ' + fs.statSync(outputFile).size + ' bytes');
  
  await browser.close();
}

main().catch(err => {
  console.error('Error:', err);
  process.exit(1);
});
