const { spawn } = require('child_process');
const path = require('path');

exports.handler = async function(event, context) {
  try {
    // Démarrer le serveur Flask
    const pythonProcess = spawn('python', ['main.py'], {
      cwd: process.cwd()
    });

    // Gérer les logs du serveur Flask
    pythonProcess.stdout.on('data', (data) => {
      console.log(`Flask stdout: ${data}`);
    });

    pythonProcess.stderr.on('data', (data) => {
      console.error(`Flask stderr: ${data}`);
    });

    // Faire une requête à l'application Flask
    const response = await fetch('http://localhost:3000/');
    const html = await response.text();

    return {
      statusCode: 200,
      headers: {
        'Content-Type': 'text/html',
      },
      body: html
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: JSON.stringify({ error: error.message })
    };
  }
}
