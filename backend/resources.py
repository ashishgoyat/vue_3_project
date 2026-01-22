from flask_restful import Api, Resource, reqparse
from models import *
from flask_security import auth_required, roles_required, current_user, roles_accepted, hash_password
from datetime import datetime, date, time
from utils import roles_list, active_required
from uuid import uuid4

api = Api()



appointment_parser = reqparse.RequestParser()
appointment_parser.add_argument('doctor_id')
appointment_parser.add_argument('patient_id')
appointment_parser.add_argument('appointment_date')
appointment_parser.add_argument('appointment_time')
appointment_parser.add_argument('status')

treatment_parser = reqparse.RequestParser()
treatment_parser.add_argument('appointment_id')
treatment_parser.add_argument('description')
treatment_parser.add_argument('diagnosis')
treatment_parser.add_argument('prescribed_medicines')
treatment_parser.add_argument('tests_recommended')
treatment_parser.add_argument('follow_up_date')
treatment_parser.add_argument('notes')

department_parser = reqparse.RequestParser()
department_parser.add_argument('name')
department_parser.add_argument('description')

doctor_parser = reqparse.RequestParser()
doctor_parser.add_argument('name')
doctor_parser.add_argument('email')
doctor_parser.add_argument('password')
doctor_parser.add_argument('age')
doctor_parser.add_argument('department_id')
doctor_parser.add_argument('specialization')
doctor_parser.add_argument('years_of_experience')
doctor_parser.add_argument('qualifications')

patient_parser = reqparse.RequestParser()
patient_parser.add_argument('name')
patient_parser.add_argument('email')
patient_parser.add_argument('password')
patient_parser.add_argument('age')

availability_parser = reqparse.RequestParser()
availability_parser.add_argument('doctor_id')
availability_parser.add_argument('day_of_week')
availability_parser.add_argument('start_time')
availability_parser.add_argument('end_time')


class AppointmentApi(Resource):

    @auth_required('token')
    @roles_accepted('admin', 'doctor', 'patient')
    @active_required
    def get(self):
        if 'admin' in roles_list(current_user.roles):
            appointments = Appointment.query.all()
        elif 'doctor' in roles_list(current_user.roles):
            appointments = Appointment.query.filter_by(doctor_id=current_user.id).all()
        else:
            appointments = Appointment.query.filter_by(patient_id=current_user.id).all()

        result = []
        
        for appointment in appointments:
            this_appointment = {}
            this_appointment['id'] = appointment.id
            this_appointment['doctor'] = appointment.doctor.name
            this_appointment['patient'] = appointment.patient.name
            this_appointment['patient_id'] = appointment.patient.id
            this_appointment['appointment_date'] = appointment.appointment_date.isoformat()
            this_appointment['appointment_time'] = appointment.appointment_time.strftime("%H:%M")
            this_appointment['status'] = str(appointment.status.value)
            result.append(this_appointment)

        if not result:
            return {'message': 'No appointments found'}, 404

        return {'appointments': result}, 200



    @auth_required('token')
    @roles_accepted('patient', 'admin')
    @active_required
    def post(self):
        args = appointment_parser.parse_args()
        try:
            appointment_date = datetime.strptime(args['appointment_date'], "%Y-%m-%d").date()
            appointment_time = datetime.strptime(args['appointment_time'], "%H:%M").time()
            if 'patient' in roles_list(current_user.roles):
                patient_id = current_user.id
            else:
                patient_id = args['patient_id']

            existing = Appointment.query.filter(
                Appointment.doctor_id == args['doctor_id'],
                Appointment.appointment_date == appointment_date,
                Appointment.appointment_time == appointment_time,
                Appointment.status != AppointmentStatus.cancelled
            ).first()

            if existing:
                return {'message': 'The selected time slot is already booked'}, 400

            appointment = Appointment(
                doctor_id = args['doctor_id'],
                patient_id = patient_id,
                appointment_date = appointment_date,
                appointment_time = appointment_time,
                status = AppointmentStatus.pending)
            db.session.add(appointment)
            db.session.commit()
            return {'message': 'Appointment created successfully'}, 201
        except:
            return {'message': 'Error creating appointment'}, 400


    @auth_required('token')
    @roles_accepted('admin', 'patient', 'doctor')
    @active_required
    def put(self , appointment_id):
        appointment = Appointment.query.get(appointment_id)
        args = appointment_parser.parse_args()
        if not appointment:
            return {'message': 'Appointment not found'}, 404
        try:
            if args['appointment_date']:
                appointment_date = datetime.strptime(args['appointment_date'], "%Y-%m-%d").date()
                appointment.appointment_date = appointment_date
            if args['appointment_time']:
                appointment_time = datetime.strptime(args['appointment_time'], "%H:%M").time()
                appointment.appointment_time = appointment_time
            if args['doctor_id']:
                appointment.doctor_id = args['doctor_id']
            if args['patient_id']:
                appointment.patient_id = args['patient_id']
            if args['status']:
                appointment.status = AppointmentStatus(args['status'].lower())

            db.session.commit()
            return {'message': 'Appointment updated successfully'}, 200

        except Exception as e:
            return {'message': 'Error updating appointment', 'error': str(e)}, 400


    @auth_required('token')
    @roles_accepted('admin', 'patient', 'doctor')
    @active_required
    def delete(self , appointment_id):
        appointment = Appointment.query.get(appointment_id)
        if appointment:
            db.session.delete(appointment)
            db.session.commit()
            return {'message': 'Appointment deleted successfully'}, 200
        else:
            return {'message': 'Appointment not found'}, 404
        


class TreatmentApi(Resource):
    @auth_required('token')
    @roles_accepted('doctor', 'patient', 'admin')
    @active_required
    def get(self, treatment_id=None):
        if treatment_id:
            treatment = Treatment.query.get(treatment_id)
            if not treatment:
                return {'message': 'Treatment not found'}, 404
            return {
                'treatment': {
                'id': treatment.id,
                'appointment_id': treatment.appointment_id,
                'description': treatment.description,
                'diagnosis': treatment.diagnosis,
                'prescribed_medicines': treatment.prescribed_medicines,
                'tests_recommended': treatment.tests_recommended,
                'follow_up_date': treatment.follow_up_date.isoformat() if treatment.follow_up_date else None,
                'notes': treatment.notes,
                'doctor': treatment.doctor.name,
                'patient': treatment.patient.name
                }
            }, 200

        if 'doctor' in roles_list(current_user.roles):
            treatments = Treatment.query.filter_by(doctor_id=current_user.id).all()
        elif( 'patient' in roles_list(current_user.roles) ):
            treatments = Treatment.query.filter_by(patient_id=current_user.id).all()
        else:
            treatments = Treatment.query.all()
        result = []
        for treatment in treatments:
            this_treatment = {}
            this_treatment['id'] = treatment.id
            this_treatment['appointment_id'] = treatment.appointment_id
            this_treatment['description'] = treatment.description
            this_treatment['diagnosis'] = treatment.diagnosis
            this_treatment['prescribed_medicines'] = treatment.prescribed_medicines
            this_treatment['tests_recommended'] = treatment.tests_recommended
            this_treatment['follow_up_date'] = treatment.follow_up_date.isoformat() if treatment.follow_up_date else None
            this_treatment['notes'] = treatment.notes
            this_treatment['created_at'] = treatment.created_at.isoformat() if treatment.created_at else None
            this_treatment['updated_at'] = treatment.updated_at.isoformat() if treatment.updated_at else None
            this_treatment['doctor'] = treatment.doctor.name
            this_treatment['patient'] = treatment.patient.name
            result.append(this_treatment)

        if not result:
            return {'message': 'No treatments found'}, 404
        
        return {'treatments': result}, 200


    @auth_required('token')
    @roles_accepted('doctor')
    @active_required
    def post(self):
        args = treatment_parser.parse_args()
        appointment = Appointment.query.get(args['appointment_id'])
        if not appointment:
            return {'message': 'Appointment not found'}, 404
        if appointment.doctor_id != current_user.id:
            return {'message': 'Unauthorized to add treatment for this appointment'}, 403
        
        treatment = Treatment(
            appointment_id = args['appointment_id'],
            doctor_id = current_user.id,
            patient_id = appointment.patient_id,
            description = args['description'],
            diagnosis = args['diagnosis'],
            prescribed_medicines = args['prescribed_medicines'],
            tests_recommended = args['tests_recommended'],
            follow_up_date = datetime.strptime(args['follow_up_date'], "%Y-%m-%d").date() if args['follow_up_date'] else None,
            notes = args['notes']
        )
        db.session.add(treatment)
        db.session.commit()

        return {'message': 'Treatment added successfully'}, 201

    @auth_required('token')
    @roles_accepted('doctor')
    @active_required
    def put(self, treatment_id):
        treatment = Treatment.query.get(treatment_id)
        args = treatment_parser.parse_args()
        if not treatment:
            return {'message': 'Treatment not found'}, 404
        if treatment.doctor_id != current_user.id:
            return {'message': 'Unauthorized to update this treatment'}, 403
        try:
            if args['description']:
                treatment.description = args['description']
            if args['diagnosis']:
                treatment.diagnosis = args['diagnosis']
            if args['prescribed_medicines']:
                treatment.prescribed_medicines = args['prescribed_medicines']
            if args['tests_recommended']:
                treatment.tests_recommended = args['tests_recommended']
            if args['follow_up_date']:
                treatment.follow_up_date = datetime.strptime(args['follow_up_date'], "%Y-%m-%d").date()
            if args['notes']:
                treatment.notes = args['notes']
            
            db.session.commit()
            return {'message': 'Treatment updated successfully'}, 200
        except Exception as e:
            return {'message': 'Error updating treatment', 'error': str(e)}, 400



class DepartmentApi(Resource):
    @auth_required('token')
    @roles_accepted('admin', 'patient', 'doctor')
    @active_required
    def get(self, department_id=None):
        if department_id:
            department = Department.query.get(department_id)
            if not department:
                return {'message': 'Department not found'}, 404
            return {
                'id': department.id,
                'name': department.name
            }, 200
        else:
            departments = Department.query.all()
            result = []
            for department in departments:
                this_department = {}
                this_department['id'] = department.id
                this_department['name'] = department.name
                this_department['description'] = department.description
                result.append(this_department)
            if not result:
                return {'message': 'No departments found'}, 404
            return {'departments': result}, 200
        

    @auth_required('token')
    @roles_required('admin')
    @active_required
    def post(self):
        args = department_parser.parse_args()
        if Department.query.filter_by(name=args['name']).first():
            return {'message': 'Department already exists'}, 400

        department = Department(name=args['name'], description=args['description'])
        db.session.add(department)
        db.session.commit()
        return {'message': 'Department created successfully'}, 201


    @auth_required('token')
    @roles_required('admin')
    @active_required
    def put(self, department_id):
        args = department_parser.parse_args()
        department = Department.query.get(department_id)
        if not department:
            return {'message': 'Department not found'}, 404
        if args['name']:
            department.name = args['name']
        if args['description']:
            department.description = args['description']
        db.session.commit()
        return {'message': 'Department updated successfully'}, 200
    


    @auth_required('token')
    @roles_required('admin')
    @active_required
    def delete(self, department_id):
        department= Department.query.get(department_id)
        if department:
            db.session.delete(department)
            db.session.commit()
            return {'message': 'Department deleted successfully'}, 200
        else:
            return {'message': 'Department not found'}, 404
        

class DoctorApi(Resource):
    @auth_required('token')
    @roles_accepted('admin', 'patient', 'doctor')
    @active_required
    def get(self, doctor_id=None):
        if doctor_id:
            doctor = User.query.filter(User.id==doctor_id, User.roles.any(name='doctor')).first()
            if not doctor:
                return {'message': 'Doctor not found'}, 404
            return {
                'id': doctor.id,
                'name': doctor.name,
                'email': doctor.email,
                'department_id': doctor.department.id if doctor.department else None,
                'age': doctor.age,
                'specialization': doctor.specialization,
                'years_of_experience': doctor.years_of_experience,
                'qualifications': doctor.qualifications,
                'active': doctor.active
            }, 200
        else:
            doctors = User.query.filter(User.roles.any(name='doctor')).all()
            result = []
            for doctor in doctors:
                this_doctor = {}
                this_doctor['id'] = doctor.id
                this_doctor['name'] = doctor.name
                this_doctor['email'] = doctor.email
                this_doctor['age'] = doctor.age
                this_doctor['department'] = doctor.department.name if doctor.department else None
                this_doctor['specialization'] = doctor.specialization
                this_doctor['years_of_experience'] = doctor.years_of_experience
                this_doctor['qualifications'] = doctor.qualifications
                this_doctor['active'] = doctor.active
                result.append(this_doctor)
            if not result:
                return {'message': 'No doctors found'}, 404
            return {'doctor': result}, 200
    

    @auth_required('token')
    @roles_required('admin')
    @active_required
    def post(self):
        args = doctor_parser.parse_args()
        if User.query.filter_by(email=args['email']).first():
            return {'message': 'Email already exists'}, 400
        department = Department.query.get(args['department_id']) if args['department_id'] else None
        doctor = User(
            name = args['name'],
            email = args['email'],
            password = hash_password(args['password']),
            age = args['age'],
            department = department,
            specialization = args['specialization'],
            years_of_experience = args['years_of_experience'],
            qualifications = args['qualifications'],
            fs_uniquifier = str(uuid4())
        )
        doctor.roles.append(Role.query.filter_by(name='doctor').first())
        db.session.add(doctor)
        db.session.commit()
        return {'message': 'Doctor created successfully'}, 201

    @auth_required('token')
    @roles_accepted('admin', 'doctor')
    @active_required
    def put(self, doctor_id):
        args = doctor_parser.parse_args()
        doctor = User.query.filter(User.id==doctor_id, User.roles.any(name='doctor')).first()
        if not doctor:
            return {'message': 'Doctor not found'}, 404
        if args['name']:
            doctor.name = args['name']
        if args['email']:
            existing_user = User.query.filter_by(email=args['email']).first()
            if existing_user and existing_user.id != doctor.id:
                return {'message': 'Email already exists'}, 400
            doctor.email = args['email']

        if args['password']:
            doctor.password = hash_password(args['password'])
        if args['age']:
            doctor.age = args['age']
        if args['department_id']:
            department = Department.query.get(args['department_id'])
            if not department:
                return {'message': 'Department not found'}, 404
            doctor.department = department
        if args['specialization']:
            doctor.specialization = args['specialization']
        if args['years_of_experience']:
            doctor.years_of_experience = args['years_of_experience']
        if args['qualifications']:
            doctor.qualifications = args['qualifications']
        
        db.session.commit()
        return {'message': 'Doctor updated successfully'}, 200

    @auth_required('token')
    @roles_required('admin')
    @active_required
    def delete(self, doctor_id):
        doctor = User.query.filter(User.id==doctor_id, User.roles.any(name='doctor')).first()
        if doctor:
            db.session.delete(doctor)
            db.session.commit()
            return {'message': 'Doctor deleted successfully'}, 200
        else:
            return {'message': 'Doctor not found'}, 404
        

class PatientApi(Resource):
    @auth_required('token')
    @roles_accepted('doctor', 'admin')
    @active_required
    def get(self, patient_id=None):
        if patient_id is None:
            patients = User.query.filter(User.roles.any(name='patient')).all()
            result = []
            for patient in patients:
                this_patient = {}
                this_patient['id'] = patient.id
                this_patient['name'] = patient.name
                this_patient['age'] = patient.age
                this_patient['email'] = patient.email
                this_patient['active'] = patient.active
                result.append(this_patient)
            return {'patients': result}, 200
        patient = User.query.filter(User.id==patient_id, User.roles.any(name='patient')).first()
        if not patient:
            return {'message': 'Patient not found'}, 404
        return {
            'id': patient.id,
            'name': patient.name,
            'age': patient.age,
            'email': patient.email,
            'active': patient.active
        }, 200
    
    @auth_required('token')
    @roles_accepted('doctor', 'admin', 'patient')
    @active_required
    def put(self, patient_id):
        args = patient_parser.parse_args()
        patient = User.query.filter(User.id==patient_id, User.roles.any(name='patient')).first()
        if not patient:
            return {'message': 'Patient not found'}, 404
        if args['name']:
            patient.name = args['name']
        if args['email']:
            existing_user = User.query.filter_by(email=args['email']).first()
            if existing_user and existing_user.id != patient.id:
                return {'message': 'Email already exists'}, 400
            patient.email = args['email']
        if args['password']:
            patient.password = hash_password(args['password'])
        if args['age']:
            patient.age = args['age']

        db.session.commit()
        return {'message': 'Patient updated successfully'}, 200
    

    @auth_required('token')
    @roles_required('admin')
    @active_required
    def delete(self, patient_id):
        patient = User.query.filter(User.id==patient_id, User.roles.any(name='patient')).first()
        if patient:
            db.session.delete(patient)
            db.session.commit()
            return {'message': 'Patient deleted successfully'}, 200
        else:
            return {'message': 'Patient not found'}, 404
        


class DoctorAvailabilityListApi(Resource):
    @auth_required('token')
    @roles_accepted('admin', 'doctor', 'patient')
    @active_required
    def get(self, doctor_id):
        doctor = User.query.get(doctor_id)
        if not doctor:
            return {'message': 'Doctor not found'}, 404
        
        slots = DoctorAvailability.query.filter_by(doctor_id=doctor_id).all()
        result = []

        for s in slots:
            result.append({
                'id': s.id,
                'day_of_week': s.day_of_week,
                'start_time': s.start_time.strftime("%H:%M"),
                'end_time': s.end_time.strftime("%H:%M")
            })
        
        return {'availability': result}, 200
    
    @auth_required('token')
    @roles_accepted('admin', 'doctor')
    @active_required
    def post(self):
        args = availability_parser.parse_args()
        
        try:
            doctor_id = args['doctor_id']
            day_of_week = args['day_of_week']
            start_time = datetime.strptime(args['start_time'], "%H:%M").time()
            end_time = datetime.strptime(args['end_time'], "%H:%M").time()
        except:
            return {'message': 'Invalid input format'}, 400
        
        if end_time <= start_time:
            return {'message': 'End time must be after start time'}, 400
        
        existing = DoctorAvailability.query.filter_by(
            doctor_id=doctor_id,
            day_of_week=day_of_week,
        ).all()

        for e in existing:
            if not (end_time <= e.start_time or start_time >= e.end_time):
                return {'message': 'Time slot overlaps with existing availability'}, 400

        slot = DoctorAvailability(
            doctor_id=doctor_id,
            day_of_week=day_of_week,
            start_time=start_time,
            end_time=end_time
        )
        db.session.add(slot)
        db.session.commit()
        return {'message': 'Availability slot created successfully'}, 201


class DoctorAvailabilitySlotApi(Resource):
    @auth_required('token')
    @roles_accepted('admin', 'doctor')
    @active_required
    def delete(self, slot_id):
        slot = DoctorAvailability.query.get(slot_id)
        if not slot:
            return {'message': 'Availability slot not found'}, 404

        db.session.delete(slot)
        db.session.commit()
        return {'message': 'Availability slot deleted successfully'}, 200


api.add_resource(AppointmentApi,'/appointments',
                                '/appointments/<int:appointment_id>')
api.add_resource(TreatmentApi,  '/treatments',
                                '/treatments/<int:treatment_id>')
api.add_resource(DepartmentApi, '/departments',
                                '/departments/<int:department_id>')
api.add_resource(DoctorApi,     '/doctors',
                                '/doctors/<int:doctor_id>')
api.add_resource(PatientApi,    '/patients',
                                '/patients/<int:patient_id>')
api.add_resource(DoctorAvailabilityListApi, '/doctor_availability',
                                        '/doctor_availability/<int:doctor_id>')
api.add_resource(DoctorAvailabilitySlotApi, '/doctor_availability/slot/<int:slot_id>')