from enum import Enum
from database import db
from flask_security import UserMixin, RoleMixin
from datetime import datetime
from sqlalchemy import UniqueConstraint

#Enum for appointment status

class AppointmentStatus(Enum):
    pending = 'pending'
    cancelled = 'cancelled'
    completed = 'completed'

# User and Role models for Flask-Security

class User (db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True )
    email = db.Column(db.String, nullable = False, unique = True)
    password = db.Column(db.String, nullable = False)
    name = db.Column(db.String, nullable = False)
    age = db.Column(db.Integer, nullable = True)

    # Doctor specific fields
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=True)
    specialization = db.Column(db.String, nullable=True)
    years_of_experience = db.Column(db.Integer, nullable=True)
    qualifications = db.Column(db.String, nullable=True)

    # for flask-security
    fs_uniquifier = db.Column(db.String, unique=True, nullable=False)
    active = db.Column(db.Boolean, default = True)  

    # Roles
    roles = db.relationship('Role', backref = 'users', secondary = 'users_roles')

    def __repr__(self):
        return f'<User {self.id} - {self.email}>'


class Role (db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String, nullable = False)
    description = db.Column(db.String, nullable = False)


class UsersRoles (db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key = True)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), primary_key = True)

# Appointment model

class Appointment (db.Model):
    id = db.Column(db.Integer, primary_key = True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False, index = True)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False, index = True)
    appointment_date = db.Column(db.Date, nullable = False)
    appointment_time = db.Column(db.Time, nullable = False)
    status = db.Column(db.Enum(AppointmentStatus, name='appointment_status'), nullable = False, default = AppointmentStatus.pending)

    doctor= db.relationship('User', foreign_keys=[doctor_id], backref = 'doctor_appointments')
    patient = db.relationship('User', foreign_keys=[patient_id], backref = 'patient_appointments')

    __table_args__ = (
        UniqueConstraint('doctor_id', 'appointment_date', 'appointment_time', name='unique_appointment'),
    )

    def __repr__(self):
        return f'<Appointment {self.id} - Doctor {self.doctor.name} - Patient {self.patient.name}>'

# Treatment model

class Treatment (db.Model):
    id = db.Column(db.Integer, primary_key = True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'), unique=True, nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    description = db.Column(db.Text, nullable=False)
    diagnosis = db.Column(db.String(255))
    prescribed_medicines = db.Column(db.Text)
    tests_recommended = db.Column(db.Text)
    follow_up_date = db.Column(db.Date)
    notes = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    # Relationships
    appointment = db.relationship('Appointment', backref=db.backref('treatment', uselist=False))
    doctor = db.relationship('User', foreign_keys=[doctor_id])
    patient = db.relationship('User', foreign_keys=[patient_id])

    def __repr__(self):
        return f'<Treatment {self.id} - Appointment {self.appointment_id}>'


class Department (db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String, nullable = False, unique = True)
    description = db.Column(db.String, nullable = True)

    doctors = db.relationship('User', backref = 'department', lazy = True)

    def __repr__(self):
        return f'<Department {self.id} - {self.name}>'
    

class DoctorAvailability (db.Model):
    id = db.Column(db.Integer, primary_key = True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    day_of_week = db.Column(db.String, nullable = False)
    start_time = db.Column(db.Time, nullable = False)
    end_time = db.Column(db.Time, nullable = False)

    doctor = db.relationship('User', backref=db.backref('availability', cascade='all, delete-orphan'))