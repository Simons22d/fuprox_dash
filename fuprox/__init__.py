from flask import Flask,request,jsonify
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy,sqlalchemy
from flask_mail import Mail
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from decouple import config
from dotenv import load_dotenv
import os

load_dotenv()

db_pass = os.getenv('DBPASS')
db_user = os.getenv("DBUSER")


app = Flask(__name__)
app.config["SECRET_KEY"] = 'ae98b899c219ea14930e01ecaafd451090f4276f6e3c20481d92d240acb35d47'
# basedir  = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+mysqlconnector://{db_user}:{db_pass}@localhost:3306/fuprox"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

try:
    db = SQLAlchemy(app)
except sqlalchemy.exc.ProgrammingError as e:
    print("error",e)

ma = Marshmallow(app)

# init bcrypt
bcrypt = Bcrypt(app)

# init the login manager
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"

# setting the config options for mail
app.config["MAIL_USERNAME"] = "denniskiruku@gmail.com"
app.config["MAIL_PASSWORD"] = "*****"
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_PORT"] = 587

mail = Mail()

from fuprox import routes
