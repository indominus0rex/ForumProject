const puppeteer = require('puppeteer');
const fs = require('fs');
const { createCanvas } = require('canvas');

const inputFile = 'C:/ForumProject/docs/images/tremor_monitor_schematic_v2.excalidraw';
const outputFile = 'C:/ForumProject/docs/images/tremor_monitor_schematic_v2.png';

async function main() {
  const excalidrawData = JSON.parse(fs.readFileSync(inputFile, 'utf8'));
  
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--disable-gpu', '--allow-file-access-from-files']
  });
  
  const page = await browser.newPage();
  await page.setViewport({ width: 1400, height: 900, deviceScaleFactor: 2 });
  
  // Build a local HTML page that uses the installed Excalidraw package
  const excalidrawPath = 'file:///' + path.resolve('./node_modules/@excalidraw/excalidraw/').replace(/\\/g, '/');
  const dataPath = excalidrawPath + '/dist/data';
  const prodPath = excalidrawPath + '/dist/prod';
  
  const html = `<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body { margin: 0; padding: 0; background: white; }
  #root { width: 100%; height: 100vh; }
</style>
<script src="${prodPath}/index.js"></script>
</head>
<body>
<div id="root"></div>
<script>
const elements = ${JSON.stringify(excalidrawData.elements)};
const appState = Object.assign({ viewBackgroundColor: '#ffffff' }, ${JSON.stringify(excalidrawData.appState || {})});

// Initialize Excalidraw app
const root = document.getElementById('root');

// Check for React
if (typeof React === 'undefined') {
  document.title = 'ERROR: React not found';
} else if (typeof ReactDOM === 'undefined') {
  document.title = 'ERROR: ReactDOM not found';
} else {
  // Try to render Excalidraw
  try {
    const ExcalidrawApp = window.ExcalidrawApp || window.default || window.Excalidraw;
    
    if (ExcalidrawApp) {
      ReactDOM.render(
        React.createElement(ExcalidrawApp, {
          initialData: {
            elements: elements,
            appState: appState,
          },
        }),
        root
      );
      document.title = 'EXPORTED';
    } else {
      // Fallback: list what's available
      document.title = 'ERROR: Available keys: ' + Object.keys(window).filter(k => k.toLowerCase().includes('excalidraw') || k === 'default').join(', ');
    }
  } catch(e) {
    document.title = 'ERROR: ' + e.message;
  }
}
</script>
</body>
</html>`;
  
  const { path } = require('path');
  
  await page.setContent(html, { waitUntil: 'networkidle0', timeout: 30000 });
  
  // Wait for render
  await page.waitForTimeout(8000);
  
  const title = await page.evaluate(() => document.title);
  console.log('Page title:', title);
  
  if (title === 'EXPORTED') {
    // Take screenshot
    await page.screenshot({ path: outputFile, fullPage: false });
    console.log('PNG exported: ' + outputFile);
    console.log('Size: ' + fs.statSync(outputFile).size + ' bytes');
  } else {
    // Try screenshot anyway
    console.log('Title was not EXPORTED, trying screenshot...');
    await page.screenshot({ path: outputFile, fullPage: false });
    console.log('Screenshot saved anyway: ' + outputFile);
    console.log('Size: ' + fs.statSync(outputFile).size + ' bytes');
  }
  
  await browser.close();
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
