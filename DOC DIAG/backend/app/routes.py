from flask import render_template, request, redirect, url_for, flash, session, jsonify
from app import app, db
from app.models import User, Diagnosis
from werkzeug.security import check_password_hash, generate_password_hash
import json

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        # Check if user already exists
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email address already registered')
            return redirect(url_for('register'))
        
        # Create new user
        new_user = User(name=name, email=email)
        new_user.set_password(password)
        
        # Add to database
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Find user
        user = User.query.filter_by(email=email).first()
        
        # Check if user exists and password is correct
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    return redirect(url_for('login'))

@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Get user's diagnosis history
    diagnoses = Diagnosis.query.filter_by(user_id=session['user_id']).order_by(Diagnosis.date.desc()).all()
    
    return render_template('home.html', diagnoses=diagnoses)

@app.route('/diagnosis', methods=['GET', 'POST'])
def diagnosis():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        symptoms = request.form['symptoms']
        heart_rate = request.form.get('heart_rate', type=int)
        pulse_rate = request.form.get('pulse_rate', type=int)
        systolic_bp = request.form.get('systolic_bp', type=int)
        diastolic_bp = request.form.get('diastolic_bp', type=int)
        temperature = request.form.get('temperature', type=float)
        
        # Process diagnosis (simple rule-based logic)
        diagnosis_result = process_diagnosis(symptoms, heart_rate, pulse_rate, systolic_bp, diastolic_bp, temperature)
        
        # Save to database
        new_diagnosis = Diagnosis(
            symptoms=symptoms,
            heart_rate=heart_rate,
            pulse_rate=pulse_rate,
            systolic_bp=systolic_bp,
            diastolic_bp=diastolic_bp,
            temperature=temperature,
            diagnosis_result=json.dumps(diagnosis_result),
            user_id=session['user_id']
        )
        
        db.session.add(new_diagnosis)
        db.session.commit()
        
        return render_template('diagnosis_result.html', diagnosis_result=diagnosis_result)
    
    return render_template('diagnosis.html')

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        # Update profile
        if 'update_profile' in request.form:
            name = request.form['name']
            email = request.form['email']
            
            # Check if email is already taken by another user
            existing_user = User.query.filter_by(email=email).first()
            if existing_user and existing_user.id != user.id:
                flash('Email already taken by another user')
                return render_template('settings.html', user=user)
            
            user.name = name
            user.email = email
            db.session.commit()
            session['user_name'] = name
            flash('Profile updated successfully')
        
        # Change password
        elif 'change_password' in request.form:
            current_password = request.form['current_password']
            new_password = request.form['new_password']
            
            if user.check_password(current_password):
                user.set_password(new_password)
                db.session.commit()
                flash('Password changed successfully')
            else:
                flash('Current password is incorrect')
    
    return render_template('settings.html', user=user)

def process_diagnosis(symptoms, heart_rate=None, pulse_rate=None, systolic_bp=None, diastolic_bp=None, temperature=None):
    """
    Severity-aware diagnosis engine with weighted scoring based on vital thresholds
    Use medical threshold rules before probability normalization.
    """
    # Split symptoms into a list
    symptom_list = [s.strip().lower() for s in symptoms.split(',')]
    
    # Initialize diseases with base probabilities
    diseases = {}
    
    # Base conditions with symptoms
    if 'fever' in symptom_list or 'temperature' in symptom_list or (temperature and temperature > 100.4):
        diseases['Influenza'] = 30
        diseases['Common Cold'] = 25
        diseases['COVID-19'] = 20
    
    if 'headache' in symptom_list:
        diseases['Migraine'] = 25
        diseases['Tension Headache'] = 20
        diseases['Sinusitis'] = 15
    
    if 'cough' in symptom_list:
        diseases['Bronchitis'] = 25
        diseases['Pneumonia'] = 20
        diseases['Asthma'] = 15
    
    if 'chest pain' in symptom_list:
        diseases['Angina'] = 30
        diseases['Heart Attack'] = 25
        diseases['GERD'] = 20
    
    # Add vital-based conditions
    diseases['Tachycardia'] = 0
    diseases['Hypertension'] = 0
    diseases['Hypertensive Crisis'] = 0
    diseases['Cardiovascular Disease'] = 0
    
    # Apply weighted scoring based on vital thresholds
    severity_score = 0
    
    # Heart rate scoring
    if heart_rate:
        if heart_rate >= 130:
            diseases['Tachycardia'] += 60  # Minimum 60% for high heart rate
            severity_score += 30
        elif heart_rate >= 100:
            diseases['Tachycardia'] += 35
            severity_score += 15
        elif heart_rate >= 80:
            diseases['Tachycardia'] += 15
    
    # Blood pressure scoring
    if systolic_bp or diastolic_bp:
        # Check for hypertensive crisis
        crisis = False
        if (systolic_bp and systolic_bp >= 180) or (diastolic_bp and diastolic_bp >= 120):
            diseases['Hypertensive Crisis'] += 85  # Increased from 70% for crisis
            crisis = True
            severity_score += 50
        elif (systolic_bp and systolic_bp >= 140) or (diastolic_bp and diastolic_bp >= 90):
            diseases['Hypertension'] += 60  # Increased from 40%
            severity_score += 30
        
        # Additional cardiovascular risk
        if systolic_bp and systolic_bp >= 140:
            diseases['Cardiovascular Disease'] += 40  # Increased from 30%
        
        # Chest pain + high BP boost - more significant boost
        if 'chest pain' in symptom_list and ((systolic_bp and systolic_bp >= 140) or (diastolic_bp and diastolic_bp >= 90)):
            diseases['Heart Attack'] += 50  # Increased from 25% boost
            severity_score += 25
    
    # Temperature scoring
    if temperature:
        if temperature >= 103:
            # Severe fever increases various infection probabilities
            if 'Influenza' in diseases:
                diseases['Influenza'] += 30  # Increased from 20%
            if 'COVID-19' in diseases:
                diseases['COVID-19'] += 25  # Increased from 15%
            severity_score += 15
        elif temperature >= 101:  # Moderate fever
            if 'Influenza' in diseases:
                diseases['Influenza'] += 15
            if 'COVID-19' in diseases:
                diseases['COVID-19'] += 10
            severity_score += 5
    
    # Combined symptom scoring for critical cases
    critical_symptoms = ['severe headache', 'chest pain', 'eye pain', 'vomiting']
    critical_count = sum(1 for symptom in critical_symptoms if symptom in symptom_list)
    
    # If we have multiple critical symptoms, significantly increase risk
    if critical_count >= 3 and ((systolic_bp and systolic_bp >= 140) or (diastolic_bp and diastolic_bp >= 90)):
        # This is a hypertensive emergency scenario
        diseases['Hypertensive Crisis'] += 70
        if 'Heart Attack' in diseases:
            diseases['Heart Attack'] += 40
        severity_score += 40
    
    # If no specific symptoms matched, provide some common defaults
    if not diseases or sum(diseases.values()) == 0:
        diseases['Common Cold'] = 30
        diseases['Allergies'] = 25
        diseases['Stress'] = 20
    
    # Emergency threshold override - force high probabilities for life-threatening conditions
    emergency_conditions = []
    
    # Check for emergency conditions with more sensitive thresholds
    if (systolic_bp and systolic_bp >= 180) or (diastolic_bp and diastolic_bp >= 120):
        emergency_conditions.append(('Hypertensive Crisis', 90))
    elif (systolic_bp and systolic_bp >= 140) or (diastolic_bp and diastolic_bp >= 90):
        # Stage 2 hypertension should trigger higher risk
        emergency_conditions.append(('Hypertension', 75))
    
    if heart_rate and heart_rate >= 130:
        emergency_conditions.append(('Tachycardia', 80))
    
    # More sensitive chest pain detection
    if 'chest pain' in symptom_list and (
        (systolic_bp and systolic_bp >= 130) or 
        (diastolic_bp and diastolic_bp >= 80) or 
        (heart_rate and heart_rate >= 90)
    ):
        emergency_conditions.append(('Heart Attack', 85))
    
    # Apply emergency overrides
    for condition, min_prob in emergency_conditions:
        if condition in diseases:
            diseases[condition] = max(diseases[condition], min_prob)
        else:
            diseases[condition] = min_prob
    
    # Ensure probabilities don't exceed 100%
    for disease in diseases:
        diseases[disease] = min(diseases[disease], 100)
    
    # Sort by probability (highest first)
    sorted_diseases = dict(sorted(diseases.items(), key=lambda item: item[1], reverse=True))
    
    # Calculate risk level based on highest probability and emergency conditions
    max_prob = max(sorted_diseases.values()) if sorted_diseases else 0
    
    # Elevate risk level for emergency conditions
    is_emergency = len(emergency_conditions) > 0
    
    # Enhanced risk classification logic
    if is_emergency and max_prob >= 70:
        risk_level = "Critical"
    elif max_prob >= 75:
        risk_level = "Critical"
    elif max_prob >= 60 or (is_emergency and max_prob >= 50):
        risk_level = "High"
    elif max_prob >= 30:
        risk_level = "Medium"
    else:
        risk_level = "Low"
    
    return {
        'diseases': sorted_diseases,
        'risk_level': risk_level,
        'is_emergency': is_emergency
    }