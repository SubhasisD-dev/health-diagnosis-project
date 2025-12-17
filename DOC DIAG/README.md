# Smart Health Diagnosis & Patient History Web App

A full-stack healthcare web application that allows patients to enter their symptoms and receive a diagnosis with probability scores, along with maintaining their medical history.

## Features

1. **User Authentication**
   - Secure user registration and login
   - Password hashing for security

2. **Home Dashboard**
   - Displays patient name
   - Shows past diagnosis history with date, symptoms, diagnosed conditions, and medicines suggested
   - Clean card-based UI with empty state handling

3. **Diagnosis System**
   - Symptom entry form with heart rate, pulse rate, blood pressure, and temperature inputs
   - Rule-based diagnosis engine that generates possible diseases with probability scores
   - Visual representation of diagnosis results with charts
   - Risk assessment indicator (Low/Medium/High chance of hospital visit)
   - Automatic saving of diagnosis results to database

4. **Settings**
   - Update profile details
   - Change password functionality
   - Logout option

## Tech Stack

- **Backend**: Python Flask
- **Database**: MySQL
- **Frontend**: HTML, Tailwind CSS, Vanilla JavaScript
- **Charts**: Chart.js

## Installation

1. Clone the repository
2. Install the required packages:
   ```
   pip install -r backend/requirements.txt
   ```
3. Set up MySQL database:
   - Create a database named `healthcare_db`
   - Update the database credentials in `backend/app/__init__.py` if needed
4. Run the application:
   ```
   cd backend
   python run.py
   ```

## Usage

1. Register for a new account or login with existing credentials
2. Navigate to the Diagnosis tab to enter your symptoms and health metrics
3. View your diagnosis results with probability scores and risk assessment
4. Check your diagnosis history on the Home dashboard
5. Update your profile or change your password in the Settings tab

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── templates/      # HTML templates
│   │   ├── static/         # Static assets (if any)
│   │   ├── __init__.py     # App initialization
│   │   ├── models.py       # Database models
│   │   └── routes.py       # Route definitions
│   ├── run.py              # Application entry point
│   └── requirements.txt    # Python dependencies
├── frontend/               # (Currently unused, all frontend in templates)
└── README.md
```

## Database Schema

The application uses two main tables:

1. **User Table**
   - id (Primary Key)
   - name
   - email (Unique)
   - password_hash

2. **Diagnosis Table**
   - id (Primary Key)
   - date
   - symptoms
   - heart_rate
   - pulse_rate
   - systolic_bp
   - diastolic_bp
   - temperature
   - diagnosis_result (JSON)
   - user_id (Foreign Key)

## Future Enhancements

- Implement more sophisticated diagnosis algorithms
- Add medication tracking
- Include doctor consultation scheduling
- Add export functionality for medical records
- Implement dark/light theme toggle