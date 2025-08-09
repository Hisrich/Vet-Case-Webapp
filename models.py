from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

class Case(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_name = db.Column(db.String(100), nullable=False)
    species = db.Column(db.String(50), nullable=False)
    breed = db.Column(db.String(50))
    gender = db.Column(db.String(50))
    age = db.Column(db.String(50))
    client_name = db.Column(db.String(50))
    client_location = db.Column(db.String(50))
    client_phone_number = db.Column(db.String(10))
    client_email = db.Column(db.String(50))
    weight = db.Column(db.String(50))
    temperature = db.Column(db.Float)
    heart_rate = db.Column(db.Integer)
    crt = db.Column(db.String(50))
    mm = db.Column(db.String(50))
    visit_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    physicalExamNotes = db.Column(db.String(250))
    presenting_complaint = db.Column(db.String(250))
    diagnosis = db.Column(db.String(50))
    treatment_given = db.Column(db.String(250))
    prescriptions = db.Column(db.String(250))
    # lab_test = db.Column(db.String(250))
    follow_up_required = db.Column(db.String(50))