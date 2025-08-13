from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_migrate import Migrate
from models import Case, db
from datetime import datetime
from dotenv import load_dotenv
import os
from flask_wtf.csrf import CSRFProtect
from google import genai
from google.genai import types
import logging
import time


load_dotenv()
app = Flask(__name__)

API_TOKEN = os.getenv("API_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = API_TOKEN
app.config['WTF_CSRF_ENABLED'] = True
client = genai.Client()

db.init_app(app)
migrate = Migrate(app, db)
csrf = CSRFProtect(app)

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/new_case", methods=["GET", "POST"])
def new_case():
    if request.method == "POST":
        try:
            data = request.get_json() if request.is_json else request.form
            
            case = Case(
                patient_name=data["patient_name"],
                species=data["species"],
                breed=data.get("breed"),
                gender=data["gender"],
                age=data.get("age"),
                client_name=data["client_name"],
                client_location=data["client_location"],
                client_phone_number=data["client_phone_number"],
                client_email=data["client_email"],
                weight=data.get("weight"),
                temperature=data.get("temperature"),
                heart_rate=data.get("heart_rate"),
                crt=data.get("crt"),
                mm=data.get("mm"),
                neutering_status=data.get("neutering_status"),
                visit_date=datetime.now(),
                physicalExamNotes=data.get("physicalExamNotes", ""),
                presenting_complaint=data.get("presenting_complaint", ""),
                diagnosis=data.get("diagnosis", ""),
                treatment_given=data.get("treatment_given", ""),
                prescriptions=data.get("prescriptions", ""),
                follow_up_required=data.get("follow_up_required", "")
            )
            
            db.session.add(case)
            db.session.commit()
            
            return jsonify({
                "success": True,
                "message": "Case added successfully"
            }), 201
            
        except Exception as e:
            db.session.rollback()
            return jsonify({
                "success": False,
                "message": str(e)
            }), 500
    
    return render_template("patient.html")


@app.route("/cases")
def list_cases():
    search_query = request.args.get('search', '').strip()
    
    if search_query:
        conditions = []
        
        text_search = f"%{search_query}%"
        conditions.extend([
            Case.patient_name.ilike(text_search),
            Case.client_name.ilike(text_search)
        ])
        
        if search_query.isdigit():
            conditions.append(Case.id == int(search_query))
        
        cases = Case.query.filter(db.or_(*conditions)).all()
    else:
        cases = Case.query.order_by(Case.visit_date.desc()).all()
        
    return render_template("cases.html", cases=cases, search_query=search_query)


@app.route("/case/<int:case_id>")
def view_case(case_id):
    case = Case.query.get_or_404(case_id)
    return render_template("view_case.html", case=case)


@app.route("/case/<int:case_id>/edit")
def edit_case(case_id):
    case = Case.query.get_or_404(case_id)
    return render_template("patient.html", case=case)


@app.route("/case/<int:case_id>/update", methods=["POST"])
def update_case(case_id):
    case = Case.query.get_or_404(case_id)

    try:
        data = request.get_json() if request.is_json else request.form
        
        case.patient_name = data["patient_name"]
        case.species = data["species"]
        case.breed = data.get("breed")
        case.gender = data["gender"]
        case.age = data.get("age")
        case.client_name = data["client_name"]
        case.client_location = data["client_location"]
        case.client_phone_number = data["client_phone_number"]
        case.client_email = data["client_email"]
        case.weight = data.get("weight")
        case.temperature = data.get("temperature")
        case.heart_rate = data.get("heart_rate")
        case.crt = data.get("crt")
        case.mm = data.get("mm")
        case.physicalExamNotes = data.get("physicalExamNotes", "")
        case.presenting_complaint = data.get("presenting_complaint", "")
        case.diagnosis = data.get("diagnosis", "")
        case.treatment_given = data.get("treatment_given", "")
        case.prescriptions = data.get("prescriptions", "")
        case.follow_up_required = data.get("follow_up_required", "")
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Case updated successfully"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


logger = logging.getLogger(__name__)
@app.route("/smartvet", methods=["GET", "POST"])
def smart_vet():
    try:
        if request.method == "POST":
            if not request.is_json:
                return jsonify({'error': 'Content-Type must be application/json'}), 415
            
            data = request.get_json()
            
            if not data:
                return jsonify({'error': 'Request body must be JSON'}), 400
            if 'prompt' not in data or not isinstance(data['prompt'], str):
                return jsonify({'error': 'Prompt must be a string'}), 400
            if not data['prompt'].strip():
                return jsonify({'error': 'Prompt cannot be empty'}), 400
            
            try:
                config = types.GenerateContentConfig(
                    system_instruction="Always start with the statement 'SmartVet! Reporting for duty!'. You are a veterinary doctor, give drugs and possible diagnosis if necessary, provide accurate veterinary information, always recommend professional consultation, never diagnose - suggest possibilities, highlight emergency symptoms, keep response under 300 words, keep the previous message in your memory so you can tailor your respond to that, resmove asterisk in your response",
                    temperature=0.7,
                    max_output_tokens=1000
                )
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[{"role": "user", "parts": [{"text": data['prompt']}]}],
                    config=config
                )
                
                if not response.text:
                    raise ValueError("Empty response from model")
                
                return jsonify({
                    'success': True,
                    'response': response.text,
                    'model': "gemini-2.5-flash",
                    'usage': {
                        'prompt_tokens': len(data['prompt'].split()),
                        'completion_tokens': len(response.text.split())
                    }
                })
                
            except Exception as e:
                logger.error(f"Model generation error: {str(e)}")
                return jsonify({
                    'success': False,
                    'error': 'Failed to generate response',
                    'details': str(e)
                }), 500
                
        return render_template("smartvet.html")
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@app.route("/smartvet/reset", methods=["POST"])
def reset_chat():
    try:
        session.pop("chat_history", None)
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Reset error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/pet-wellness')
def pet_wellness():
    return render_template('pet_wellness.html')


@app.route('/vaccinations')
def vaccinations():
    return render_template('vaccinations.html')


if __name__ == "__main__":
    app.run(debug=True)