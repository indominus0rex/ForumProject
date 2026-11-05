const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

const inputFile = 'C:/ForumProject/docs/images/tremor_monitor_schematic_v2.excalidraw';
const outputFile = 'C:/ForumProject/docs/images/tremor_monitor_schematic_v2.png';

async function main() {
  const excalidrawData = JSON.parse(fs.readFileSync(inputFile, 'utf8'));
  
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--disable-gpu']
  });
  
  const page = await browser.newPage();
  await page.setViewport({ width: 1400, height: 900, deviceScaleFactor: 2 });
  
  // Create a self-contained HTML page that uses Excalidraw's export utilities
  const html = `<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body { margin: 0; padding: 0; background: white; }
  canvas { display: block; }
</style>
</head>
<body>
<canvas id="output"></canvas>
<script type="module">
import { exportToCanvas } from 'https://cdn.jsdelivr.net/npm/@excalidraw/excalidraw@latest/dist/excalidraw.production.min.js';

const elements = ${JSON.stringify(excalidrawData.elements)};
const appState = Object.assign({ viewBackgroundColor: '#ffffff' }, ${JSON.stringify(excalidrawData.appState || {})});

// Create a mock canvas context for export
const canvas = document.getElementById('output');
canvas.width = 1400;
canvas.height = 900;

exportToCanvas({
  elements: elements,
  appState: appState,
  files: null,
  canvas: canvas,
  exportPadding: 20,
  scale: 2,
}).then(() => {
  console.log('Export complete');
  document.title = 'EXPORTED';
}).catch(err => {
  console.error('Export error:', err);
  document.title = 'ERROR: ' + err.message;
});
</script>
</body>
</html>`;
  
  await page.setContent(html, { waitUntil: 'networkidle0', timeout: 60000 });
  
  // Wait for export to complete
  await page.waitForFunction(() => document.title === 'EXPORTED' || document.title.startsWith('ERROR'), { timeout: 30000 });
  
  const title = await page.evaluate(() => document.title);
  
  if (title === 'EXPORTED') {
    // Get the canvas data
    const dataUrl = await page.evaluate(() => {
      const canvas = document.getElementById('output');
      return canvas.toDataURL('image/png');
    });
    
    const base64 = dataUrl.replace(/^data:image\/png;base64,/, '');
    fs.writeFileSync(outputFile, Buffer.from(base64, 'base64'));
    console.log('PNG exported: ' + outputFile);
    console.log('Size: ' + fs.statSync(outputFile).size + ' bytes');
  } else {
    console.error('Export failed:', title);
    process.exit(1);
  }
  
  await browser.close();
}

main().catch(err => {
  console.error('Error:', err);
  process.exit(1);
});
