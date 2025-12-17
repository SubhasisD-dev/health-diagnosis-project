from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Relationship with diagnoses
    diagnoses = db.relationship('Diagnosis', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def __repr__(self):
        return f"User('{self.name}', '{self.email}')"

class Diagnosis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    symptoms = db.Column(db.Text, nullable=False)
    heart_rate = db.Column(db.Integer, nullable=True)
    pulse_rate = db.Column(db.Integer, nullable=True)
    systolic_bp = db.Column(db.Integer, nullable=True)
    diastolic_bp = db.Column(db.Integer, nullable=True)
    temperature = db.Column(db.Float, nullable=True)
    diagnosis_result = db.Column(db.JSON, nullable=False)  # Store as JSON
    
    # Foreign key to user
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):
        return f"Diagnosis('{self.date}', '{self.user_id}')"