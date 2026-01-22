from flask import Flask
from config import LocalDevelopmentConfig
from models import User, Role
from database import db
from resources import api
from flask_cors import CORS
from flask_security import Security, SQLAlchemyUserDatastore
from flask_security import hash_password
from datetime import datetime
from celery_tasks.celery_init import celery_init_app


def createApp():
    app = Flask(__name__)

    app.config.from_object(LocalDevelopmentConfig)

    CORS(app)

    db.init_app(app)
    api.init_app(app)

    datastore = SQLAlchemyUserDatastore(db, User, Role)
    app.security = Security(app, datastore = datastore)
    app.app_context().push()

    with app.app_context():
        db.create_all()

        app.security.datastore.find_or_create_role(name='admin', description='Owner of hospital')
        app.security.datastore.find_or_create_role(name='doctor', description='Doctor in hospital')
        app.security.datastore.find_or_create_role(name='patient', description='Patient in hospital')
        db.session.commit()

        if not app.security.datastore.find_user(email='admin@hospital.in'):
            app.security.datastore.create_user(
                email='admin@hospital.in',
                password= hash_password('admin'),
                name='admin',
                roles=['admin'])

        if not app.security.datastore.find_user(email='doctor01@hospital.in'):
            app.security.datastore.create_user(
                email='doctor01@hospital.in',
                password= hash_password('doctor'),
                name='Doctor',
                age=27,
                roles=['doctor'],
                specialization='Cardiology',
                qualifications='MBBS, MD',
                years_of_experience=5)

        if not app.security.datastore.find_user(email='patient01@hospital.in'):
            app.security.datastore.create_user(
                email='patient01@hospital.in',
                password= hash_password('patient'),
                name='Ashish',
                age=19,
                roles=['patient'])
        db.session.commit()
    return app


app = createApp()
celery = celery_init_app(app)


from routes import *

if __name__ == '__main__':
    app.run()
