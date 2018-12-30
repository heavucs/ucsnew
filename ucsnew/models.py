from flask_sqlalchemy import SQLAlchemy
from .application import app
from decimal import Decimal, ROUND_HALF_UP
import datetime

db = SQLAlchemy(app)

class DictableBase:

    def as_dict(self):
        dict = {}
        for c in self.__table__.columns:
            dict[c.name] = getattr(self, c.name)

        return dict

class Member(db.Model, DictableBase):
    __tablename__ = 'members'
    __table_args__ = {'mysql_engine': 'InnoDB'}

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

class Item(db.Model, DictableBase):
    __tablename__ = 'items'
    __table_args__ = {'mysql_engine': 'InnoDB'}

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
        resource_d['membernumber'] = self.members.membernumber

        return resource_d

    def __repr__(self):
        return "<Item %r>" % self.ItemNumber

class User(db.Model, DictableBase):
    __tablename__ = 'users'
    __table_args__ = {'mysql_engine': 'InnoDB'}

    username = db.Column(db.String(64), primary_key=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    firstname = db.Column(db.String(255))
    lastname = db.Column(db.String(255))

    def __init__(self, username, password, firstname, lastname):
        self.username = str(username)
        self.password = str(password)
        self.firstname = str(firstname)
        self.lastname = str(lastname)

    def as_api_dict(self):

        resource_d = self.as_dict()

        return resource_d

    def __repr__(self):
        return '<User %r>' % self.username

class UserRoles(db.Model, DictableBase):
    __tablename__ = 'userroles'
    __table_args__ = {'mysql_engine': 'InnoDB'}

    #id = db.Column(db.Integer, primary_key=True, auto_increment=True)
    #username = db.Column(db.String(64), nullable=False)
    rolename = db.Column(db.String(255), primary_key=True, nullable=False)

    users_username = db.Column(db.String(64), db.ForeignKey('users.username'), primary_key=True, nullable=False)
    username = db.relationship(User, backref=db.backref('users', uselist=True,
                                cascade='all, delete-orphan'))

    def __init__(self, username, rolename):
        self.username = str(username)
        self.rolename = str(rolename)

    def as_api_dict(self):

        resource_d = self.as_dict()
        resource_d['username'] = self.users.username

        return resource_d

    def __repr__(self):
        return '<Role(user:%s,role:%s)>' % (self.username, self.rolename)
