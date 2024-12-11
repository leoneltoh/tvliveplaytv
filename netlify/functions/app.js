const { spawn } = require('child_process');
const serverless = require('serverless-http');
const express = require('express');
const app = express();

// Middleware pour parser le JSON
app.use(express.json());

// Route principale
app.get('/', (req, res) => {
  const python = spawn('python', ['main.py']);
  
  let dataString = '';
  
  python.stdout.on('data', (data) => {
    dataString += data.toString();
  });
  
  python.stderr.on('data', (data) => {
    console.error(`Error: ${data}`);
  });
  
  python.on('close', (code) => {
    res.send(dataString);
  });
});

// Export the serverless function
module.exports.handler = serverless(app);
