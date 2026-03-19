const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('projectBoardApi', {
  getDefaultDocument: () => ipcRenderer.invoke('document:get-default'),
  openJson: () => ipcRenderer.invoke('dialog:open-json'),
  saveJson: (payload) => ipcRenderer.invoke('dialog:save-json', payload),
  setAlwaysOnTop: (value) => ipcRenderer.invoke('window:set-always-on-top', value),
  getAlwaysOnTop: () => ipcRenderer.invoke('window:get-always-on-top')
});
