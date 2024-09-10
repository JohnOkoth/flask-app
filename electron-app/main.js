const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

function createWindow() {
  let win = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      nodeIntegration: true,
    },
  });

  win.loadURL('http://127.0.0.1:5000');  // URL for the Flask app
}

app.whenReady().then(() => {
  // Adjust the path to point to the correct location of app.py
  const flaskApp = spawn('python', ['../app.py']);  // Now pointing to the parent folder
  
  flaskApp.stdout.on('data', (data) => {
    console.log(`stdout: ${data}`);
  });

  flaskApp.stderr.on('data', (data) => {
    console.error(`stderr: ${data}`);
  });

  flaskApp.on('close', (code) => {
    console.log(`child process exited with code ${code}`);
  });

  createWindow();
});
