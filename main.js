const { app, BrowserWindow, dialog, ipcMain } = require('electron');
const path = require('path');
const fs = require('fs/promises');

const DEFAULT_DOCUMENT = {
  title: 'Project Spacing Board',
  columns: ['Road Name', 'Category', 'Arrangement', 'Spacing'],
  rows: [
    {
      id: `${Date.now()}`,
      values: {
        'Road Name': 'Marketing Site',
        Category: 'Desktop',
        Arrangement: 'Hero / Cards / Footer',
        Spacing: '8 / 16 / 24 / 48'
      }
    }
  ]
};

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1380,
    height: 900,
    minWidth: 1000,
    minHeight: 700,
    backgroundColor: '#0b1020',
    title: 'Project Spacing Board',
    autoHideMenuBar: true,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false
    }
  });

  mainWindow.loadFile('index.html');
}

app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

ipcMain.handle('window:set-always-on-top', (_event, value) => {
  if (!mainWindow) {
    return false;
  }

  mainWindow.setAlwaysOnTop(Boolean(value), 'screen-saver');
  return mainWindow.isAlwaysOnTop();
});

ipcMain.handle('window:get-always-on-top', () => {
  return mainWindow?.isAlwaysOnTop() ?? false;
});

ipcMain.handle('dialog:open-json', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    title: 'Open board JSON',
    properties: ['openFile'],
    filters: [{ name: 'JSON Files', extensions: ['json'] }]
  });

  if (result.canceled || result.filePaths.length === 0) {
    return { canceled: true };
  }

  const filePath = result.filePaths[0];
  const content = await fs.readFile(filePath, 'utf8');
  const parsed = JSON.parse(content);

  return {
    canceled: false,
    filePath,
    data: parsed
  };
});

ipcMain.handle('dialog:save-json', async (_event, payload) => {
  const { suggestedPath, data } = payload;
  const result = await dialog.showSaveDialog(mainWindow, {
    title: 'Save board JSON',
    defaultPath: suggestedPath || 'project-spacing-board.json',
    filters: [{ name: 'JSON Files', extensions: ['json'] }]
  });

  if (result.canceled || !result.filePath) {
    return { canceled: true };
  }

  await fs.writeFile(result.filePath, `${JSON.stringify(data, null, 2)}\n`, 'utf8');

  return {
    canceled: false,
    filePath: result.filePath
  };
});

ipcMain.handle('document:get-default', () => {
  return structuredClone(DEFAULT_DOCUMENT);
});
