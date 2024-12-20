const serverless = require('serverless-http');
const express = require('express');
const app = express();

// Import your main app
const mainApp = require('../../main.py');

// Use the main app
app.use('/', mainApp);

// Export the serverless function
exports.handler = serverless(app);
