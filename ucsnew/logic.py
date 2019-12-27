import datetime
import re
import barcode
from io import BytesIO
import MySQLdb as sql
from decimal import Decimal, ROUND_HALF_UP

#from collections import deque

from .models import db
from .models import Member
from .models import Item
from .models import Transaction
from .models import User

from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import BadRequest      # 400
from werkzeug.exceptions import Unauthorized    # 401
from werkzeug.exceptions import Forbidden       # 403
from werkzeug.exceptions import NotFound        # 404

from .application import app


### Business logic for Member DAOs

def get_members_list(q_membernumber=None, q_lastname=None, q_phonenumber=None,
        page=1, per_page=25):

    if q_phonenumber == None: q_phonenumber = ""

    page = page if page else 1
    per_page = per_page if per_page else 25

    db_member = (
                db.session.query(Member)
                .order_by(Member.membernumber.asc())
            )
    if q_membernumber:
        db_member = db_member.filter(Member.membernumber.like("{}%%"
                .format(q_membernumber)))
    if q_lastname:
        db_member = db_member.filter(Member.lastname.like("{}%%"
                .format(q_lastname)))
    if q_phonenumber:
        db_member = db_member.filter(Member.phone.like("{}%%"
                .format(q_phonenumber)))

    if not app.config['LEGACY_UCS_ENABLED']:
        pagination = db_member.paginate(page=page, per_page=per_page,
            error_out=False)
        members_l = pagination.items
    else:
        pagination = db_member.paginate(page=page, per_page=per_page,
            error_out=False)
        members_l = pagination.items
        #members_l = db_member.all()

        legacy_db = sql.connect(
                host=app.config['LEGACY_UCS_SQLHOST'],
                user=app.config['LEGACY_UCS_SQLUSER'],
                passwd=app.config['LEGACY_UCS_SQLPASS'],
                db=app.config['LEGACY_UCS_SQLDB']
                )
        legacy_db.c = legacy_db.cursor()
        nullstring = lambda x: x if x else ''
        legacy_db.c.execute("""SELECT MemberNumber, Established, FirstName,
                LastName, Address, Address2, City, State, Zip, Phone, Email,
                Password, Question, Answer, ActivationCode, Activated, Admin,
                Browser, Notification FROM Account {} {} {} limit {},{}"""
                    .format(
                        "WHERE MemberNumber like \"{}%%\""
                            .format(nullstring(q_membernumber)),
                        "AND LastName like \"{}%%\""
                            .format(nullstring(q_lastname)),
                        "AND Phone like \"{}%%\""
                            .format(nullstring(q_phonenumber)),
                        (page * per_page - per_page),
                        per_page,
                        )
                    )
        legacy_members_l = legacy_db.c.fetchall()

        for i in legacy_members_l:
            member = {
                'membernumber': i[0],
                'established': i[1],
                'firstname': i[2],
                'lastname': i[3],
                'address': i[4],
                'address2': i[5],
                'city': i[6],
                'state': i[7],
                'zip': i[8],
                'phone': i[9],
                'email': i[10],
                'password': i[11],
                'question': i[12],
                'answer': i[13],
                'activationcode': i[14],
                'activated': i[15],
                'admin': i[16],
                'browser': i[17],
                'notification': i[18],
                }
            members_l.append(member)

        #members_l = members_l[int(0 + (page - 1) * per_page):int(page * per_page)]

    return members_l

def create_member(payload):

    new_member_d = {
            'membernumber': payload['membernumber'],
            'established': datetime.date.today(),
            'firstname': payload['firstname'],
            'lastname': payload['lastname'],
            'address': payload['address'],
            'address2': payload['address2'],
            'city': payload['city'],
            'state': payload['state'],
            'zipcode': payload['zipcode'],
            'phone': payload['phone'],
            'email': payload['email'],
            'password': payload['password'],
            'question': payload['question'],
            'answer': payload['answer'],
            'activationcode': payload['activationcode'],
            'admin': str(payload['admin']),
            }

    new_member = Member(
            new_member_d['membernumber'],
            new_member_d['established'],
            new_member_d['firstname'],
            new_member_d['lastname'],
            new_member_d['address'],
            new_member_d['address2'],
            new_member_d['city'],
            new_member_d['state'],
            new_member_d['zipcode'],
            new_member_d['phone'],
            new_member_d['email'],
            new_member_d['password'],
            new_member_d['question'],
            new_member_d['answer'],
            new_member_d['activationcode'],
            new_member_d['admin'],
            )
   
    try:
        db.session.add(new_member)
        db.session.commit()

        new_member_d = new_member.as_api_dict()
        # Created as an error since I'm not getting info messages
        app.logger.error("Created account {}: {} {}"
                .format(
                    new_member.membernumber,
                    new_member.firstname,
                    new_member.lastname,
                    )
                )

    except IntegrityError as e:
        app.logger.error("IntegrityError: {}".format(e))
        raise Forbidden("Unable to create resource: IntegrityError")

    return new_member


### Business logic for Item DAOs

def get_items_list(q_itemnumber=None, q_membernumber=None, q_description=None,
        page=1, per_page=25):

    page = page if page else 1
    per_page = per_page if per_page else 25

    db_item = (
                db.session.query(Item)
                .order_by(Item.itemnumber.asc())
            )
    if q_itemnumber:
        db_item = db_item.filter(Item.itemnumber.like("{}%%"
                .format(q_itemnumber)))
    if q_membernumber:
        db_item = db_item.filter(Item.member_membernumber.like("{}%%"
                .format(q_membernumber)))
    if q_description:
        db_item = db_item.filter(Item.description.like("%%{}%%"
                .format(q_description)))

    if not app.config['LEGACY_UCS_ENABLED']:
        pagination = db_item.paginate(page=page, per_page=per_page,
            error_out=False)
        items_l = pagination.items
    else:
        pagination = db_item.paginate(page=page, per_page=per_page,
            error_out=False)
        items_l = pagination.items
        #items_l = db_item.all()

        legacy_db = sql.connect(
                host=app.config['LEGACY_UCS_SQLHOST'],
                user=app.config['LEGACY_UCS_SQLUSER'],
                passwd=app.config['LEGACY_UCS_SQLPASS'],
                db=app.config['LEGACY_UCS_SQLDB']
                )
        legacy_db.c = legacy_db.cursor()
        nullstring = lambda x: x if x else ''
        legacy_db.c.execute("""SELECT ID, ItemNumber, Description, Category,
                Subject, Publisher, Year, ISBN, `Condition`, ConditionDetail,
                NumItems, FridayPrice, SaturdayPrice, Donate, CheckedIn,
                CheckedOut, Status, Deleted, MemberNumber
                FROM Item {} {} {} ORDER BY ID limit {},{}"""
                    .format(
                        "WHERE ItemNumber like \"{}%%\""
                            .format(nullstring(q_itemnumber)),
                        "AND Description like \"%%{}%%\""
                            .format(nullstring(q_description)),
                        "AND MemberNumber like \"{}%%\""
                            .format(nullstring(q_membernumber)),
                        (page * per_page - per_page),
                        per_page,
                        )
                    )
        legacy_items_l = legacy_db.c.fetchall()

        for i in legacy_items_l:
            formatprice = lambda x: str(Decimal(x).quantize(Decimal('0.01'),
                rounding=ROUND_HALF_UP))
            def formattime(t):
                re_datetime = r'(\d{4})-(\d{2})-(\d{2})( (\d{2}):(\d{2}):(\d{2}))?'
                t = re.match(re_datetime, t)
                if t:
                    if len(t.groups()) >= 8:
                        t = str(datetime.datetime.strptime(str(t.group(0)),
                            '%Y-%m-%d %H:%M:%S'))
                    else:
                        t = datetime.datetime.strptime(str(t.group(0)), '%Y-%m-%d')
                        t = t.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    t = '0000-00-00 00:00:00'

                return t

            item = {
                'itemnumber': i[0],
                'description': i[2],
                'category': i[3],
                'subject': i[4],
                'publisher': i[5],
                'year': i[6],
                'isbn': i[7],
                'condition': int(i[8]),
                'conditiondetail': i[9],
                'numitems': int(i[10]),
                'price': formatprice(str(i[11])),
                'discountprice': formatprice(str(i[12])),
                'donate': int(i[13]),
                'checkedin': formattime(str(i[14])),
                'checkedout': formattime(str(i[15])),
                'status': i[16],
                'deleted': int(i[17]),
                'membernumber': i[18],
                }
            items_l.append(item)

        #items_l = items_l[int(0 + (page - 1) * per_page):int(page * per_page)]

    return items_l

def create_item(payload):

    itemnumber = (int(Item.query.count()) + 1)

    new_item_d = {
            'itemnumber': str(itemnumber),
            'membernumber': payload['membernumber'],
            'description': payload['description'],
            'category': payload['category'],
            'subject': payload['subject'],
            'publisher': payload['publisher'],
            'year': payload['year'],
            'isbn': payload['isbn'],
            'condition': payload['condition'],
            'conditiondetail': payload['conditiondetail'],
            'numitems': payload['numitems'],
            'price': Decimal(str(payload['price'])) \
                    .quantize(Decimal(".01"), ROUND_HALF_UP),
            'discountprice': Decimal(str(payload['discountprice'])) \
                    .quantize(Decimal(".01"), ROUND_HALF_UP),
            'donate': payload['donate'],
            }

    new_item = Item(
            new_item_d['itemnumber'],
            new_item_d['membernumber'],
            new_item_d['description'],
            new_item_d['category'],
            new_item_d['subject'],
            new_item_d['publisher'],
            new_item_d['year'],
            new_item_d['isbn'],
            new_item_d['condition'],
            new_item_d['conditiondetail'],
            new_item_d['numitems'],
            new_item_d['price'],
            new_item_d['discountprice'],
            new_item_d['donate'],
            )

    try:
        db.session.add(new_item)
        db.session.commit()

        new_item = (
                Item.query
                    .filter(Item.MemberNumber == payload['MemberNumber'])
                    .filter(Item.ItemNumber == itemnumber)
                    .first()
                )

        # Created as an error since I'm not getting info messages
        app.logger.error("Created item {}: {}"
                .format(
                    new_item.ID,
                    new_item.Description
                    )
                )

    except IntegrityError as e:
        app.logger.error("IntegrityError: {}".format(e))
        raise Forbidden("Unable to create resource: IntegrityError")

    return new_item


### Business logic for Transaction DAOs

def get_transactions_list(q_username=None, q_itemnumber=None, q_transactionnumber=None,
        page=1, per_page=25):

    page = page if page else 1
    per_page = per_page if per_page else 25

    db_transaction = (
                db.session.query(Transaction)
                .order_by(Transaction.uuid.asc())
            )
    if q_username:
        db_transaction = db_transaction.filter(Transaction.user_username.like("{}%%"
                .format(q_username)))
    if q_itemnumber:
        db_transaction = db_transaction.filter(Transaction.items.like("%%{}%%"
                .format(q_itemnumber)))
    if q_transactionnumber:
        db_transaction = db_transaction.filter(Transaction.uuid.like("%%{}%%"
                .format(q_transactionnumber)))

    if not app.config['LEGACY_UCS_ENABLED']:
        pagination = db_transaction.paginate(page=page, per_page=per_page,
            error_out=False)
        transactions_l = pagination.items
    else:
        pagination = db_transaction.paginate(page=page, per_page=per_page,
            error_out=False)
        transactions_l = pagination.items
        #transactions_l = db_transaction.all()

        legacy_db = sql.connect(
                host=app.config['LEGACY_UCS_SQLHOST'],
                user=app.config['LEGACY_UCS_SQLUSER'],
                passwd=app.config['LEGACY_UCS_SQLPASS'],
                db=app.config['LEGACY_UCS_SQLDB']
                )
        legacy_db.c = legacy_db.cursor()
        nullstring = lambda x: x if x else ''

        legacy_db.c.execute("""SELECT ID, Date, Checker, Status, Payment_Type,
                    Payment_Note, Payment_Amount, Total
                FROM Transaction
                RIGHT JOIN (
                    SELECT DISTINCT(TransactionID)
                    FROM Transaction_Record
                    {}) as Transaction_Record
                ON Transaction.ID = Transaction_Record.TransactionID
                {} {}
                ORDER BY ID
                LIMIT {},{};"""
                        .format(
                            "WHERE ItemID like \"{}%%\""
                                .format(nullstring(q_itemnumber)),
                            "WHERE Checker like \"{}%%\""
                                .format(nullstring(q_username)),
                            "AND ID like \"{}%%\""
                                .format(nullstring(q_transactionnumber)),
                            (page * per_page - per_page),
                            per_page,
                            )
                        )
        legacy_transactions_l = legacy_db.c.fetchall()

        for i in legacy_transactions_l:
            formatprice = lambda x: str(Decimal(x).quantize(Decimal('0.01'),
                rounding=ROUND_HALF_UP))

            transaction = {
                'uuid': str(i[0]),
                'datetime': str(i[1]),
                'user_username': i[2],
                'finalized': i[3],
                'payment_method': i[4],
                #'total': formatprice(str(i[7])),
                'total': str(i[7]),
                }
            transactions_l.append(transaction)

        #transactions_l = transactions_l[int(0 + (page - 1) * per_page):int(page * per_page)]

    return transactions_l


### Business logic for Item DAOs

from werkzeug.security import check_password_hash, generate_password_hash

def get_users_list():

    users_l = User.query.all()

    return users_l

def get_user(username):

    db_user = User.query.filter(User.username == username).first()

    if db_user is not None:
        return db_user.as_api_dict()
    else:
        raise NotFound("Resource user %s not found" % username)

def create_user(payload):

    new_user = {
            'username': str(payload['username']),
            'password': generate_password_hash(str(payload['password']),
                app.config['PW_HASH']),
            'firstname': str(payload['firstname']),
            'lastname': str(payload['lastname']),
            }

    db_user = User(
        new_user['username'],
        new_user['password'],
        new_user['firstname'],
        new_user['lastname'],
    )
   
    try:
        db.session.add(db_user)
        db.session.commit()

        db_user = User.query.\
            filter(User.username == new_user['username']).\
            first()

        app.logger.info("Created user %s" % db_user.username)
        # Created as an error since I'm not getting info messages
        app.logger.error("Created user %s" % (db_user.username))

    except IntegrityError as e:
        app.logger.error("IntegrityError: %s" % str(e))
        raise Forbidden("Unable to create resource: IntegrityError")

    return db_user

def replace_user(auth_user, old_username, payload):

    db_user = User.query.filter(User.username == old_username).first()
    if not db_user:
        raise NotFound

    if 'password' in payload:
        payload['password'] = generate_password_hash(
                str(payload['password']), app.config['PW_HASH']
                )

    new_user = {
            'username': payload.get('username', db_user.username),
            'password': payload.get('password', db_user.password),
            'firstname': payload.get('firstname', db_user.firstname),
            'lastname': payload.get('lastname', db_user.lastname),
            }

    db_user.username = new_user.get('username',db_user.username)
    db_user.password = new_user.get('password',db_user.password)
    db_user.firstname = new_user.get('firstname',db_user.firstname)
    db_user.lastname = new_user.get('lastname',db_user.lastname)
   
    try:
        db.session.commit()

        db_user = User.query.filter(User.username == new_user['username']).first()

        app.logger.info("Replaced user %s with %s" % \
                (old_username, db_user.username))
        # Created as an error since I'm not getting info messages
        app.logger.error("Replaced user %s with %s" % \
                (old_username, db_user.username))

    except IntegrityError as e:
        app.logger.error("IntegrityError: %s" % str(e))
        raise Forbidden("Unable to replace resource: IntegrityError")

    return db_user

def delete_user(auth_user, old_username, payload):

    db_user = User.query.filter(User.username == old_username).first()
    if not db_user:
        raise NotFound

    try:
        db.session.delete(db_user)
        db.session.commit()

        app.logger.info("Deleted user %s" % old_username)
        # Created as an error since I'm not getting info messages
        app.logger.error("Deleted user %s" % old_username)

    except IntegrityError as e:
        app.logger.error("IntegrityError: %s" % str(e))
        raise Forbidden("Unable to delete resource: IntegrityError")

    return {'message': "User %s successfully deleted by %s" % \
            (old_username, auth_user)}


### Business logic for Barcode DAOs

def generate_barcode(code):

    if app.config['BARCODE_SYMBOLOGY'] in barcode.PROVIDED_BARCODES:

        app.logger.info("Generating barcode for {}".format(code))

        imgstore = {}
        imgstore['MEM'] = BytesIO()
        imgstore['FILE'] = "{}/{}".format(
                app.config['BARCODE_TEMPDIR'],
                code
                )

        barcode_img = imgstore[app.config['BARCODE_STORAGE']]
        barcode.generate(
            app.config['BARCODE_SYMBOLOGY'],
            code,
            output=barcode_img
            )
    else:
        app.logger.error("Unknown Barcode Symbology: {}".format(
            app.config['BARCODE_SYMBOLOGY'])
            )
        app.logger.error("Set config BARCODE_SYMBOLOGY to one of the following:")
        app.logger.error("{}".format(PROVIDES_BARCODES))

    if app.config['BARCODE_STORAGE'] == 'FILE':
        f = open("{}.svg".format(imgstore['FILE']), 'rb')
        barcode_img = BytesIO(f.read())

    barcode_img.seek(0)

    return barcode_img

def get_barcodes_list():

    barcode_l = list()

    return barcode_l

#def create_barcode(payload):
def create_barcode(barcode_number):

    return generate_barcode(barcode_number)
