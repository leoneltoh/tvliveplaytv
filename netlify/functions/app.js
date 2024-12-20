const { PythonShell } = require('python-shell');
const path = require('path');

exports.handler = async function(event, context) {
  try {
    let options = {
      mode: 'json',
      pythonPath: process.env.PYTHON_PATH || 'python3.9',
      pythonOptions: ['-u'],
      scriptPath: __dirname,
      args: [JSON.stringify(event)]
    };

    return new Promise((resolve, reject) => {
      PythonShell.run('app.py', options, function (err, results) {
        if (err) {
          console.error('Error:', err);
          resolve({
            statusCode: 500,
            body: JSON.stringify({ error: err.message })
          });
        } else {
          const response = results[results.length - 1];
          resolve(response);
        }
      });
    });
  } catch (error) {
    return {
      statusCode: 500,
      body: JSON.stringify({ error: error.message })
    };
  }
}
