from flask_sqlalchemy import SQLAlchemy
from .application import app
from decimal import Decimal, ROUND_HALF_UP
import datetime

db = SQLAlchemy(app)

class Member(db.Model):
    __tablename__ = 'members'
    __table_args__ = {'mysql_engine': 'InnoDB'}

    id = db.Column(db.Integer, unique=True, autoincrement=True)
    membernumber = db.Column(db.String(255), primary_key=True)
    established = db.Column(db.Date)
    firstname = db.Column(db.String(255))
    lastname = db.Column(db.String(255))
    address = db.Column(db.String(255))
    address2 = db.Column(db.String(255))
    city = db.Column(db.String(255))
    state = db.Column(db.String(2))
    zipcode = db.Column(db.String(5))
    phone = db.Column(db.String(10))
    email = db.Column(db.String(255))
    password = db.Column(db.String(255))
    question = db.Column(db.String(255))
    answer = db.Column(db.String(255))
    activationcode = db.Column(db.String(255))
    activated = db.Column(db.Date)
    admin = db.Column(db.String(1), default='0')
    browser = db.Column(db.String(255))
    notification = db.Column(db.String(1))

    def __init__(self, membernumber, firstname, lastname, address, address2, city, state, zipcode, phone, email, password, question, answer, activationcode, admin):
        self.membernumber = str(membernumber)
        self.established = datetime.datetime.now().date()
        self.firstname = str(firstname)
        self.lastname = str(lastname)
        self.address = str(address)
        self.address2 = str(address2)
        self.city = str(city)
        self.state = str(state)
        self.zipcode = str(zipcode)
        self.phone = str(phone)
        self.email = str(email)
        self.password = str(password)
        self.question = str(question)
        self.answer = str(answer)
        self.activationcode = str(activationcode)
        self.admin = str(admin)

    def as_api_dict(self):

        resource_d = self.as_dict()

        return resource_d

    def __repr__(self):
        return "<Member %s>" % self.membernumber

class Item(db.Model):
    __tablename__ = 'items'
    __table_args__ = {'mysql_engine': 'InnoDB'}

    id = db.Column(db.Integer, unique=True, autoincrement=True)
    itemnumber = db.Column(db.String(255), primary_key=True)
    description = db.Column(db.String(255))
    category = db.Column(db.String(255))
    subject = db.Column(db.String(255))
    publisher = db.Column(db.String(255))
    year = db.Column(db.String(4))
    isbn = db.Column(db.String(16))
    condition = db.Column(db.String(1))
    conditiondetail = db.Column(db.String(255))
    numitems = db.Column(db.String(4))
    price = db.Column(db.DECIMAL(11,4))
    discountprice = db.Column(db.DECIMAL(11,4))
    donate = db.Column(db.String(1), default='0')
    checkedin = db.Column(db.Date)
    checkedout = db.Column(db.Date)
    status = db.Column(db.String(1), default='0')
    deleted = db.Column(db.String(1))

    members_membernumber = db.Column(db.String(255), db.ForeignKey('members.membernumber'), nullable=False)
    membernumber = db.relationship(Member, backref=db.backref('members', uselist=True,
                                cascade='all, delete-orphan'))

    def __init__(self, itemnumber, membernumber, description, category, subject, publisher, year, isbn, condition, conditiondetail, numitems, price, discountprice, donate):
        itemnumber = str(itemnumber)
        membernumber = str(membernumber)
        description = str(description)
        category = str(category)
        subject = str(subject)
        publisher = str(publisher)
        year = str(year)
        isbn = str(isbn)
        condition = str(condition)
        conditiondetail = str(conditiondetail)
        numitems = str(numitems)
        price = Decimal(price).quantize(Decimal('0.0001', rounding=ROUND_HALF_UP))
        discountprice = Decimal(discountprice).quantize(Decimal('0.0001', rounding=ROUND_HALF_UP))
        donate = str(donate)

    def as_api_dict(self):

        resource_d = self.as_dict()
        resource_d['membernumber'] = self.membernumber.membernumber

        return resource_d

    def __repr__(self):
        return "<Item %r>" % self.ItemNumber

#class Checker(db.Model):
#    __tablename__ = 'Checkers'
#    __table_args__ = {'mysql_engine': 'InnoDB'}
#
#    ID = db.Column(db.Integer, primary_key=True)
#    LoginID = db.Column(db.Unicode(32), unique=True, nullable=False)
#    FirstName = db.Column(db.Unicode(32), nullable=False)
#    LastName = db.Column(db.Unicode(32), nullable=False)
#    Barcode = db.Column(db.Integer, nullable=False)
#    Admin = db.Column(db.Boolean, nullable=False, default=False)
#    #Admin = db.Column(db.Integer(1), nullable=False, Default=0)
#
#    def __init__(self, LoginID, FirstName, LastName, Barcode, Admin):
#        self.LoginID = LoginID
#        self.FirstName = FirstName
#        self.LastName = LastName
#        self.Barcode = Barcode
#        self.Admin = Admin
#
#    def __repr__(self):
#        return '<Checker %r>' % self.ID

