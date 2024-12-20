from flask import Flask, send_file, jsonify, request
from flask_socketio import SocketIO
import json
import os

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

def handler(event, context):
    """Netlify Function handler"""
    try:
        # Récupérer le chemin de la requête
        path = event.get('path', '/')
        
        # Simuler une requête Flask
        with app.test_client() as client:
            response = client.get(path)
            
            return {
                "statusCode": response.status_code,
                "headers": {
                    "Content-Type": "text/html",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": response.get_data(as_text=True)
            }
            
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

# Importer les routes de main.py
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from main import app as main_app

# Copier les routes de l'application principale
app.register_blueprint(main_app)

if __name__ == '__main__':
    app.run()
