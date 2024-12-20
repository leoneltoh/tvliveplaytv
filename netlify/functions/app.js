const { PythonShell } = require('python-shell');

exports.handler = async function(event, context) {
  try {
    let options = {
      mode: 'text',
      pythonPath: 'python',
      pythonOptions: ['-u'],
      scriptPath: '.',
      args: []
    };

    let pyshell = new PythonShell('main.py', options);

    return {
      statusCode: 200,
      headers: {
        'Content-Type': 'text/html'
      },
      body: `
        <!DOCTYPE html>
        <html>
          <head>
            <meta charset="utf-8">
            <title>TV Live</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
          </head>
          <body>
            <div id="app"></div>
            <script src="/player.html"></script>
          </body>
        </html>
      `
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: JSON.stringify({ error: error.message })
    };
  }
}
