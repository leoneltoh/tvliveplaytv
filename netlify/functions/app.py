from flask import Flask, send_file, jsonify, request
from flask_socketio import SocketIO
import json

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

def handler(event, context):
    """Netlify Function handler"""
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "text/html",
        },
        "body": app.send_static_file('player.html')
    }

if __name__ == '__main__':
    app.run()
