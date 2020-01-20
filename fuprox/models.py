from fuprox import db,ma,login_manager,app
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# we are going to create the model from a user class
# the user mixen adds certain fields that are required matain the use session
# it will add certain fileds to the user class tha are essential to the user login
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(12), unique=True, nullable=False)
    email = db.Column(db.String(48), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default="default.jpg")
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"User (' {self.id} ',' {self.username} ', '{self.email}', '{self.image_file}' )"

    def __init__(self,username,email,password):
        self.username = username
        self.email = email
        self.password = password


# creating a company class
class Company(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(length=50))
    service = db.Column(db.String(length=250))

    def __init__(self,name,service):
        self.name = name
        self.service = service

    def __repr__(self):
        return f"Company {self.name} -> {self.service}"



# creating a branch class
class Branch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(length=100))
    company = db.Column(db.String(length=11))
    longitude = db.Column(db.String(length=50))
    latitude = db.Column(db.String(length=50))
    opens = db.Column(db.String(length=50))
    closes = db.Column(db.String(length=50))
    service = db.Column(db.String(length=50))
    description = db.Column(db.String(length=50))


    def __init__(self, name, company, longitude, latitude,opens,closes,service,description):
        self.name = name
        self.company = company
        self.longitude = longitude
        self.latitude = latitude
        self.opens = opens
        self.closes = closes
        self.service = service
        self.description = description


# creating a user class
# creating a company class
class Service(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(length=50))
    service = db.Column(db.String(length=250))

    def __init__(self,name,service):
        self.name = name
        self.service = service

    def __repr__(self):
        return f"Company {self.name} -> {self.service}"


class Help(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(length=100), nullable=False, unique=True)
    title = db.Column(db.String(length=250), nullable=False)
    solution = db.Column(db.Text, nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, topic, title, solution):
        self.topic = topic
        self.title = title
        self.solution = solution


# defining a class for topics
class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(length=100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, name, description):
        self.name = name
        self.description = description


