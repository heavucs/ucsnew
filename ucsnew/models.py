from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref
from decimal import Decimal
from decimal import ROUND_HALF_UP
import datetime
import uuid

db = SQLAlchemy()
app = current_app

Transaction_Item = db.Table('transaction_item', db.Model.metadata,
            db.Column('transaction_uuid', db.String(36),
                db.ForeignKey('transactions.uuid')),
            db.Column('item_uuid', db.String(36),
                db.ForeignKey('items.uuid')),
            mysql_engine='InnoDB',
            mysql_charset='utf8mb4',
        )

class DictableBase:

    def as_dict(self):
        dict = {}
        for c in self.__table__.columns:
            dict[c.name] = getattr(self, c.name)

        return dict


class Member(db.Model, DictableBase):
    __tablename__ = 'members'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'}

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
    activated = db.Column(db.Date, nullable=True)
    admin = db.Column(db.String(1), default='0')
    browser = db.Column(db.String(255))
    notification = db.Column(db.String(1))

    def __init__(self, membernumber, established, firstname, lastname, address,
            address2, city, state, zipcode, phone, email, password, question,
            answer, activationcode, admin):

        self.membernumber = str(membernumber)
        self.established = established
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
        self.admin = int(admin)

    def as_api_dict(self):

        resource_d = self.as_dict()

        return resource_d

    def __repr__(self):
        return "<Member {}>".format(self.membernumber)

class Item(db.Model, DictableBase):
    __tablename__ = 'items'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'}

    uuid = db.Column(db.String(36), primary_key=True, default=uuid.uuid4())
    itemnumber = db.Column(db.String(255))
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

    member_membernumber = db.Column(db.String(255),
                            db.ForeignKey('members.membernumber'))
    membernumber = db.relationship(Member,
            backref=backref("items", cascade="all,delete"))

    def __init__(self, uuid, itemnumber, membernumber, description, category,
            subject, publisher, year, isbn, condition, conditiondetail,
            numitems, price, discountprice, donate):

        self.uuid = str(uuid)
        self.itemnumber = str(itemnumber)
        self.member_membernumber = str(membernumber)
        self.description = str(description)
        self.category = str(category)
        self.subject = str(subject)
        self.publisher = str(publisher)
        self.year = str(year)
        self.isbn = str(isbn)
        self.condition = str(condition)
        self.conditiondetail = str(conditiondetail)
        self.numitems = str(numitems)
        self.price = Decimal(price).quantize(Decimal('0.0001'),
                rounding=ROUND_HALF_UP)
        self.discountprice = Decimal(discountprice).quantize(Decimal('0.0001'),
                rounding=ROUND_HALF_UP)
        self.donate = str(donate)

    def as_api_dict(self):

        resource_d = self.as_dict()

        return resource_d

    def __repr__(self):
        return "<Item {}>".format(self.uuid)

class User(db.Model, DictableBase):
    __tablename__ = 'users'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'}

    username = db.Column(db.String(64), primary_key=True)
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

@db.event.listens_for(User.__table__, 'after_create')
def insert_initial_values(*args, **kwargs):

    """Initializes admin user when application is started for the first time"""

    from werkzeug.security import generate_password_hash

    new_user = {
            'username': 'admin',
            'password': generate_password_hash('admin',
                app.config['PW_HASH']),
            'firstname': '',
            'lastname': '',
            }

    db.session.add(User(
        new_user['username'],
        new_user['password'],
        new_user['firstname'],
        new_user['lastname'],
        ))

    db.session.commit()


#class UserRoles(db.Model, DictableBase):
#    __tablename__ = 'userroles'
#    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4',}
#
#    #id = db.Column(db.Integer, primary_key=True, auto_increment=True)
#    #username = db.Column(db.String(64), nullable=False)
#    rolename = db.Column(db.String(255), primary_key=True, nullable=False)
#
#    users_username = db.Column(db.String(64), db.ForeignKey('users.username'),
#            primary_key=True, nullable=False)
#    username = db.relationship(User, backref=db.backref('users', uselist=True,
#                                cascade='all, delete-orphan'))
#
#    def __init__(self, username, rolename):
#        self.username = str(username)
#        self.rolename = str(rolename)
#
#    def as_api_dict(self):
#
#        resource_d = self.as_dict()
#        resource_d['username'] = self.users.username
#
#        return resource_d
#
#    def __repr__(self):
#        return '<Role(user:%s,role:%s)>' % (self.username, self.rolename)

class Transaction(db.Model, DictableBase):
    __tablename__ = 'transactions'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'}

    uuid = db.Column(db.String(36), primary_key=True, default=uuid.uuid4())
    ctime = db.Column(db.DateTime, default=datetime.datetime.now())
    ftime = db.Column(db.DateTime, nullable=True)
    finalized = db.Column(db.Boolean, default=False) #0 False, 1 True
    payment_method = db.Column(db.String(1))
    total = db.Column(db.DECIMAL(11,4))

    # NOTE: Transactions should never be deleted in the event that a user is delete
    user_username = db.Column(db.String(64), db.ForeignKey('users.username'))
    user = db.relationship("User", backref="transactions")

    items = db.relationship("Item",
                secondary=Transaction_Item,
                backref='transactions')

    def __init__(self, user, finalized, ftime, payment_method,
            payment_note, total):

        self.uuid = str(uuid.uuid4())
        self.ctime = datetime.datetime.now() #Creation time
        self.ftime = ftime                   #Finalization time
        self.user_username = str(user)
        self.finalized = finalized
        self.payment_method = str(payment_method)
        self.payment_note = str(payment_note)
        self.total = Decimal(total).quantize(Decimal('0.0001'),
                        rounding=ROUND_HALF_UP)

    def as_api_dict(self):

        resource_d = self.as_dict()

        return resource_d

    def __repr__(self):
        return "<Transaction {}>".format(self.uuid)

class AuditLog(db.Model, DictableBase):
    __tablename__ = 'auditlogs'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'}

    uuid = db.Column(db.String(36), primary_key=True, default=uuid.uuid4())
    ctime = db.Column(db.DateTime, default=datetime.datetime.now())
    user = db.Column(db.String(64), nullable=False) # This is a cc of username
    text = db.Column(db.Text())

    def __init__(self, user, text):

        self.uuid = str(uuid.uuid4())
        self.ctime = datetime.datetime.now()
        self.user = str(user)
        self.text = str(text)

    def as_api_dict(self):

        resource_d = self.as_dict()

        return resource_d

    def __repr__(self):
        return "<AuditLog {}>".format(self.uuid)

class AuditLogTag(db.Model, DictableBase):
    __tablename__ = 'auditlogtags'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'}

    uuid = db.Column(db.String(36), primary_key=True, default=uuid.uuid4())
    ctime = db.Column(db.DateTime, default=datetime.datetime.now())
    tag = db.Column(db.String(255), index=True, nullable=False)
    tagtype = db.Column(db.String(255))

    auditlog_uuid = db.Column(db.String(255),
                            db.ForeignKey('auditlogs.uuid'))
    auditlog = db.relationship(AuditLog,
            backref=backref("auditlogtags", cascade="all,delete"))

    def __init__(self, auditlog_uuid, tag, tagtype=None):

        self.uuid = str(uuid.uuid4())
        self.ctime = datetime.datetime.now()
        self.auditlog_uuid = str(auditlog_uuid)
        self.tag = str(tag)
        self.tagtype = str(tagtype)

    def as_api_dict(self):

        resource_d = self.as_dict()

        return resource_d

    def __repr__(self):
        return "<AuditLogTag {}>".format(self.uuid)
