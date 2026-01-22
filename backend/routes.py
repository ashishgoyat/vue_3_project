from flask import current_app as app, jsonify, request, render_template, flash
from flask_security import auth_required, roles_required, current_user, roles_accepted, login_user
from sqlalchemy import distinct
from flask_security.utils import verify_password, hash_password
from database import db
from datetime import datetime, date, time
from models import *
from utils import roles_list, active_required



@app.route('/')
def index():
    return render_template('index.html')


@app.get('/api/admin')
@auth_required('token')
@roles_required('admin')
def admin_home():
    return jsonify({'message': 'Welcome, Admin!'}), 200


@app.get('/api/home')
@auth_required('token')
@roles_accepted('patient', 'admin', 'doctor')
@active_required
def user_home():
    user = current_user
    return jsonify({
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'roles': roles_list(user.roles)
    })

# Authentication and Registration

@app.post('/api/register')
def create_user():
    data = request.get_json()
    if not data or not all(k in data for k in ('name', 'email', 'password', 'age')):
        return jsonify({'message': 'Missing required fields'}), 400
    
    if app.security.datastore.find_user(email=data['email']):
        return jsonify({'message': 'User already exists'}), 400
    
    role = app.security.datastore.find_role('patient')
    if not role:
        return jsonify({'message': 'Role not found'}), 404
    
    app.security.datastore.create_user(
        name=data['name'],
        email=data['email'],
        password=hash_password(data['password']),
        age=data['age'],
        roles=[role]
    )
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201

@app.post('/api/login')
def login():
    data = request.get_json()
    if not data or not all(k in data for k in ('email', 'password')):
        return jsonify({'message': 'Missing required fields'}), 400
    
    user = app.security.datastore.find_user(email=data['email'])
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    if not verify_password(data['password'], user.password):
        return jsonify({'message': 'Invalid password'}), 401
    
    if not user.active:
        return jsonify({'message': 'User account is inactive'}), 403
    
    login_user(user)

    return jsonify({
        'message': 'Login successful',
        'auth-token': user.get_auth_token(),
        'id': user.id,
        'roles': roles_list(user.roles)
    }), 200



@app.get('/api/patient_history/<int:appointment_id>')
@auth_required('token')
@roles_accepted('doctor', 'admin')
@active_required
def get_patient_history(appointment_id):
    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        return {"message": "Appointment not found"}, 404

    patient = User.query.get(appointment.patient_id)
    if not patient:
        return {"message": "Patient not found"}, 404
        
    # Fetch medical records (if model exists)
    medical_records = Treatment.query.filter_by(appointment_id=appointment.id).all()
    record_list = []
    for rec in medical_records:
        record_list.append({
            "id": rec.id,
            "doctor": rec.doctor.name,
            "patient": rec.patient.name,
            "diagnosis": rec.diagnosis,
            "prescribed_medicines": rec.prescribed_medicines,
            "tests": rec.tests_recommended,
            "follow_up_date": rec.follow_up_date.strftime('%Y-%m-%d') if rec.follow_up_date else None,
            "notes": rec.notes,
        })
    
    # Combine everything
    response = {
        "id": appointment.id,
        "appointment_date": appointment.appointment_date.strftime('%Y-%m-%d'),
        "medical_records": record_list
    }

    return jsonify(response)



@app.get('/api/patient_details/<int:patient_id>')
@auth_required('token')
@roles_accepted('doctor', 'patient')
@active_required
def get_patient_details(patient_id):
    patient = User.query.get(patient_id)
    if not patient:
        return {"message": "Patient not found"}, 404

    appointments = Appointment.query.filter_by(patient_id=patient_id).all()
    treatments = Treatment.query.filter_by(patient_id=patient_id).all()

    def serialize_appointment(appt):
        return {
            "id": appt.id,
            "doctor": appt.doctor.name if appt.doctor else "Unknown",
            "date": appt.appointment_date.strftime("%Y-%m-%d"),
            "time": appt.appointment_time.strftime("%H:%M") if appt.appointment_time else "N/A",
            "status": str(appt.status.name if hasattr(appt.status, 'name') else appt.status or "Scheduled")
        }

    def serialize_treatment(treat):
        return {
            "id": treat.id,
            "description": treat.description,
            "diagnosis": treat.diagnosis,
            "prescription": treat.prescribed_medicines,
            "tests": treat.tests_recommended,
            "follow_up_date": treat.follow_up_date.strftime('%Y-%m-%d') if treat.follow_up_date else None,
            "notes": treat.notes
        }

    return {
        "patient": {
            "id": patient.id,
            "name": patient.name,
        },
        "appointments": [serialize_appointment(a) for a in appointments],
        "treatments": [serialize_treatment(t) for t in treatments]
    }, 200




@app.get('/api/doctor_dashboard')
@auth_required('token')
@roles_required('doctor')
@active_required
def doctor_dashboard():
    doctor_id = current_user.id

    # Upcoming appointments
    upcoming = Appointment.query.filter(
        Appointment.doctor_id == doctor_id,
        (Appointment.appointment_date == date.today()) & (Appointment.appointment_time >= datetime.now().time()),
        Appointment.status == 'pending'
    ).all()

    # Unique patients assigned to this doctor (from any past appointment)
    patient_ids = db.session.query(distinct(Appointment.patient_id)).filter(
        Appointment.doctor_id == doctor_id,
        Appointment.appointment_date <= date.today(),
        Appointment.status == 'completed',
        Appointment.patient_id.isnot(None)
    ).all()

    # Get actual patient objects
    patients = [User.query.get(pid[0]) for pid in patient_ids]

    def serialize_appointment(appt):
        return {
            "id": appt.id,
            "patient_name": appt.patient.name if appt.patient else "Unknown",
            "date": appt.appointment_date.strftime("%Y-%m-%d"),
            "time": appt.appointment_time.strftime("%H:%M") if appt.appointment_time else "N/A",
            "status": str(appt.status.name if hasattr(appt.status, 'name') else appt.status or "Scheduled")
        }

    def serialize_patient(patient):
        return {
            "id": patient.id,
            "name": patient.name,
            "email": patient.email,
        }

    return {
        "upcoming_appointments": [serialize_appointment(a) for a in upcoming],
        "assigned_patients": [serialize_patient(p) for p in patients]
    }, 200



@app.get('/api/patient_dashboard')
@auth_required('token')
@roles_required('patient')
@active_required
def patient_dashboard():
    patient = current_user
    patient_data = {
        "id": patient.id,
        "name": patient.name,
        "email": patient.email,
        "age": patient.age
    }

    # Get all the departments
    departments = Department.query.all()
    department_list = []
    for dept in departments:
        doctors = User.query.filter(
            User.roles.any(name='doctor'),
            User.department_id == dept.id
        ).all()

        doctor_list = []
        for doc in doctors:
            doctor_list.append({
                "id": doc.id,
                "name": doc.name,
                "specialization": doc.specialization
            })

        department_list.append({
            "id": dept.id,
            "name": dept.name,
            "doctors": doctor_list,
            "description": dept.description
        })

    # Upcoming appointments for the patient
    appointments = Appointment.query.filter(
        Appointment.appointment_date >= date.today(),
        Appointment.status != 'rejected',
        Appointment.patient_id == patient.id
    ).all()
    upcoming = []
    for appt in appointments:
        upcoming.append({
            "id": appt.id,
            "doctor": appt.doctor.name,
            "date": appt.appointment_date.strftime("%Y-%m-%d"),
            "time": appt.appointment_time.strftime("%H:%M"),
            "department": appt.doctor.department.name,
            "status": str(appt.status.value if hasattr(appt.status, 'value') else appt.status)
        })

    return {
        "patient": patient_data,
        "departments": department_list,
        "upcoming_appointments": upcoming
    }, 200


@app.put('/api/toggle_user_active/<int:user_id>')
@auth_required('token')
@roles_required('admin')
@active_required
def toggle_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    user.active = not user.active
    db.session.commit()
    return jsonify({'message': 'User status updated successfully', 'active': user.active}), 200