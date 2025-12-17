from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import json

# Initialize the app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///healthcare.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Custom filter for JSON parsing
@app.template_filter('from_json')
def from_json(value):
    try:
        return json.loads(value)
    except:
        return {}

# Initialize database
db = SQLAlchemy(app)

from app import routes