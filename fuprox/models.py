from datetime import datetime
from flask_login import UserMixin
import secrets
from fuprox import db, ma, login_manager


def ticket_unique() -> int:
    return secrets.token_hex(16)


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

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password


# creating a company class


class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(length=50), unique=True)
    service = db.Column(db.String(length=250))

    def __init__(self, name, service):
        self.name = name
        self.service = service

    def __repr__(self):
        return f"Company {self.name} -> {self.service}"


class CompanySchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "service")


# creating a branch class

# creating a branch class
class Branch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(length=250), unique=True)
    company = db.Column(db.String(length=100), db.ForeignKey("company.name"), nullable=False)
    longitude = db.Column(db.String(length=50))
    latitude = db.Column(db.String(length=50))
    opens = db.Column(db.String(length=50))
    closes = db.Column(db.String(length=50))
    service = db.Column(db.String(length=100), db.ForeignKey("service.name"))
    description = db.Column(db.String(length=50))
    key_ = db.Column(db.Text)
    valid_till = db.Column(db.DateTime)
    is_synced = db.Column(db.Boolean, default=False)
    unique_id = db.Column(db.String(255), default=ticket_unique, unique=True)

    def __init__(self, name, company, longitude, latitude, opens, closes, service, description, key_):
        self.name = name
        self.company = company
        self.longitude = longitude
        self.latitude = latitude
        self.opens = opens
        self.closes = closes
        self.service = service
        self.description = description
        self.key_ = key_


# creating branch Schema
class BranchSchema(ma.Schema):
    class Meta:
        fields = (
            'id', 'name', 'company', 'address', 'longitude', 'latitude', 'opens', 'closes', 'service', 'description',
            "key_", "valid_till","unique_id")


# creating a user class
# creating a company class
class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(length=50), unique=True)
    service = db.Column(db.String(length=250))
    is_medical = db.Column(db.Boolean, default=False)

    def __init__(self, name, service, is_medical):
        self.name = name
        self.service = service
        self.is_medical = is_medical


class ServiceSchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "service", "is_medical")


class Help(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(length=100), nullable=False, unique=True)
    title = db.Column(db.String(length=250), nullable=False)
    solution = db.Column(db.Text, nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.now, nullable=False)

    def __init__(self, topic, title, solution):
        self.topic = topic
        self.title = title
        self.solution = solution


class Mpesa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=True)
    receipt_number = db.Column(db.String(255), nullable=True)
    transaction_date = db.Column(db.String(255), nullable=True)
    phone_number = db.Column(db.Integer, nullable=True)
    checkout_request_id = db.Column(db.String(255), nullable=True)
    merchant_request_id = db.Column(db.String(255), nullable=True)
    result_code = db.Column(db.Integer, nullable=False)
    result_desc = db.Column(db.Text, nullable=True)
    local_transactional_key = db.Column(db.String(255), nullable=False)

    def __init__(self, MerchantRequestID, CheckoutRequestID, ResultCode, ResultDesc):
        self.merchant_request_id = MerchantRequestID
        self.checkout_request_id = CheckoutRequestID
        self.result_code = ResultCode
        self.result_desc = ResultDesc


class MpesaSchema(ma.Schema):
    class Meta:
        fields = ("id", "amount", "receipt_number", "transaction_date", "phone_number", "checkout_request_id",
                  "merchant_request_id", "result_code", "result_desc", "date_added", "local_transactional_key")


# creating a booking ID
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_name = db.Column(db.String(length=250), nullable=True)
    start = db.Column(db.String(length=200))
    branch_id = db.Column(db.Integer)
    ticket = db.Column(db.String(length=6), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.now, unique=True)
    active = db.Column(db.Boolean, default=False, nullable=False)
    nxt = db.Column(db.Integer, nullable=False, default=1001)
    serviced = db.Column(db.Boolean, nullable=False, default=False)
    teller = db.Column(db.String(200), nullable=False, default=000000)
    kind = db.Column(db.Integer, nullable=False)
    user = db.Column(db.Integer)
    is_instant = db.Column(db.Boolean, default=False)
    forwarded = db.Column(db.Boolean, default=False)

    def __init__(self, service_name, start, branch_id, ticket, active, nxt, serviced, teller, kind, user,
                 instant, fowarded):
        self.service_name = service_name
        self.start = start
        self.branch_id = branch_id
        self.ticket = ticket
        self.active = active
        self.nxt = nxt
        self.serviced = serviced
        self.teller = teller
        self.kind = kind
        self.user = user
        self.is_instant = instant
        self.forwarded = fowarded
        self.nxt = 1001


class BookingSchema(ma.Schema):
    class Meta:
        fields = (
        "id", "service_name", "start", "branch_id", "ticket", "active", "next", "serviced", "teller", "kind", "user",
        "is_instant", "forwarded", "")


class ImageCompany(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.ForeignKey("company.id"), nullable=False)
    image = db.Column(db.String(length=250), nullable=False)

    def __init__(self, company, image):
        self.company = company
        self.image = image


class ImageCompanySchema(ma.Schema):
    class Meta:
        fields = ("id", "company", "image")
