// Excalidraw PNG export script using puppeteer
const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

const inputFile = 'C:/ForumProject/docs/images/tremor_monitor_schematic_v2.excalidraw';
const outputFile = 'C:/ForumProject/docs/images/tremor_monitor_schematic_v2.png';

async function main() {
  const excalidrawData = fs.readFileSync(inputFile, 'utf8');
  
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
  });
  
  const page = await browser.newPage();
  await page.setViewport({ width: 1400, height: 900, deviceScaleFactor: 2 });
  
  // Create HTML page that loads Excalidraw and renders our diagram
  const html = `<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body { margin: 0; padding: 0; background: white; }
  #root { width: 100%; height: 100vh; }
</style>
</head>
<body>
<div id="root"></div>
<script>
window.EXCALIDRAW_ASSET_PATH = 'file:///C:/ForumProject/excalidraw-build/node_modules/@excalidraw/excalidraw/dist/';
</script>
<script src="file:///C:/ForumProject/excalidraw-build/node_modules/@excalidraw/excalidraw/dist/excalidraw.production.min.js"></script>
<script src="file:///C:/ForumProject/excalidraw-build/node_modules/@excalidraw/excalidraw/dist/excalidraw.development.js"></script>
<script>
const data = ${excalidrawData};

// Wait for Excalidraw to be ready
async function init() {
  const root = document.getElementById('root');
  
  // Use the exported renderExcalidraw function
  if (typeof ExcalidrawApp !== 'undefined') {
    ReactDOM.render(
      React.createElement(ExcalidrawApp, {
        initialData: {
          elements: data.elements,
          appState: Object.assign({ viewBackgroundColor: '#ffffff' }, data.appState || {}),
        },
      }),
      root
    );
  } else if (typeof React !== 'undefined' && typeof ReactDOM !== 'undefined') {
    // Try to find the main export
    const excalidrawLib = window.Excalidraw || window.ReactComponent || window.default;
    if (excalidrawLib) {
      ReactDOM.render(
        React.createElement(excalidrawLib, {
          initialData: {
            elements: data.elements,
            appState: Object.assign({ viewBackgroundColor: '#ffffff' }, data.appState || {}),
          },
        }),
        root
      );
    } else {
      root.innerHTML = '<h1>Could not find Excalidraw export</h1>';
    }
  } else {
    root.innerHTML = '<h1>React not available</h1>';
  }
}

// Wait a bit for scripts to load
setTimeout(init, 1000);

// Set a flag when ready
window.excalidrawReady = true;
</script>
</body>
</html>`;
  
  await page.setContent(html, { waitUntil: 'networkidle0', timeout: 30000 });
  
  // Wait for the diagram to render
  await page.waitForTimeout(5000);
  
  // Try to get the canvas element and export it
  const dataUrl = await page.evaluate(() => {
    const canvas = document.querySelector('canvas');
    if (canvas) {
      return canvas.toDataURL('image/png');
    }
    // Fallback: return null
    return null;
  });
  
  if (dataUrl) {
    const base64 = dataUrl.replace(/^data:image\/png;base64,/, '');
    fs.writeFileSync(outputFile, Buffer.from(base64, 'base64'));
    console.log('PNG exported successfully: ' + outputFile);
  } else {
    // Take a screenshot as fallback
    await page.screenshot({ path: outputFile, fullPage: false });
    console.log('Screenshot saved: ' + outputFile);
  }
  
  await browser.close();
}

main().catch(err => {
  console.error('Error:', err);
  process.exit(1);
});
