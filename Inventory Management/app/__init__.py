from flask import Flask 
from flask_mail import Mail, Message
from flask_moment import Moment
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv
import os
from config import basedir

#force loading of environment variables
load_dotenv('.flaskenv')

#Gets the environment variable from .flaskenv
PASSWORD = os.environ.get('DATABASE_PASSWORD')
USERNAME = os.environ.get('DATABASE_USERNAME')
DB_NAME = os.environ.get('DATABASE_NAME')

app = Flask(__name__)

app.config.from_object('config')
app.config['SECRET_KEY'] = 'csc400'
app.config['UPLOADS_FOLDER'] = os.path.join(
    basedir, 'static')
#Add Database configuration
# app.config['SQLALCHEMY_DATABASE_URI'] = ('mysql+pymysql://'
#                                          + USERNAME
#                                          + ':'
#                                          + PASSWORD
#                                          + '@db4free.net/'
#                                          + DB_NAME)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost:3306/zack'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]= True

app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 465,
    MAIL_USE_TSL = False,
    MAIL_USE_SSL = True,
    MAIL_USERNAME = 'zackehrnfeltcsc@gmail.com', 
    MAIL_PASSWORD = 'Daisy1222',
    MAIL_DEFAULT_SENDER = ('RESA Power Inventory','zackehrnfeltcsc@gmail.com'),
    SECRET_KEY = 'some secret key')
mail = Mail(app)
moment = Moment(app)
bootstrap = Bootstrap(app)

#Create Database connection and associate it with the Flask application
db = SQLAlchemy(app)

login = LoginManager(app)

#enables @login_required
login.login_view = 'login'

#Add models
from app import routes, models
from app.models import User


#Create Database Schema
# db.create_all()

#Create Admin and Regular User

