from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_migrate import Migrate
from models import Case, db
from datetime import datetime
from dotenv import load_dotenv
import os
from flask_wtf.csrf import CSRFProtect

load_dotenv()
app = Flask(__name__)

API_TOKEN = os.getenv("API_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = API_TOKEN
app.config['WTF_CSRF_ENABLED'] = True

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
                neutering_status = data.get("neutering_status"),
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
        # Build the query conditions
        conditions = []
        
        # Add text search conditions for name fields
        text_search = f"%{search_query}%"
        conditions.extend([
            Case.patient_name.ilike(text_search),
            Case.client_name.ilike(text_search)
        ])
        
        # Add numeric ID condition only if search_query is numeric
        if search_query.isdigit():
            conditions.append(Case.id == int(search_query))
        
        # Apply all conditions with OR
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

@app.route("/case/<int:case_id>/update", methods = ["POST"])
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
    
@app.route('/animal-care')
def animal_care():
    return render_template('animal_care.html')

@app.route('/pet-wellness')
def pet_wellness():
    return render_template('pet_wellness.html')

@app.route('/vaccinations')
def vaccinations():
    return render_template('vaccinations.html')

if __name__ == "__main__":
    app.run(debug=True)