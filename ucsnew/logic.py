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
from sqlalchemy.orm.exc import NoResultFound
from werkzeug.exceptions import BadRequest      # 400
from werkzeug.exceptions import Unauthorized    # 401
from werkzeug.exceptions import Forbidden       # 403
from werkzeug.exceptions import NotFound        # 404
from werkzeug.security import generate_password_hash

from .application import app


### Business logic for Member DAOs

def get_members(q_membernumber=None, q_lastname=None, q_phonenumber=None,
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

    pagination = db_member.paginate(page=page, per_page=per_page,
        error_out=False)
    members_l = pagination.items

    if app.config['LEGACY_UCS_ENABLED']:

        nullstring = lambda x: x if x else ''

        legacy_db = sql.connect(
                host=app.config['LEGACY_UCS_SQLHOST'],
                user=app.config['LEGACY_UCS_SQLUSER'],
                passwd=app.config['LEGACY_UCS_SQLPASS'],
                db=app.config['LEGACY_UCS_SQLDB']
                )

        legacy_db.c = legacy_db.cursor()
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

    return members_l

def create_member(payload):

    new_member_d = {
            'membernumber': str(payload['membernumber']),
            'established': str(datetime.date.today()),
            'firstname': str(payload['firstname']),
            'lastname': str(payload['lastname']),
            'address': str(payload['address']),
            'address2': str(payload['address2']),
            'city': str(payload['city']),
            'state': str(payload['state']),
            'zipcode': str(payload['zipcode']),
            'phone': str(payload['phone']),
            'email': str(payload['email']),
            'password': str(payload['password']),
            'question': str(payload['question']),
            'answer': str(payload['answer']),
            'activationcode': str(payload['activationcode']),
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
        app.logger.info("Created member {}: {} {}"
                .format(
                    new_member.membernumber,
                    new_member.firstname,
                    new_member.lastname,
                    )
                )

    except IntegrityError as e:
        app.logger.error("IntegrityError: {}".format(e))
        raise Forbidden("Unable to create member: IntegrityError")

    return new_member

def replace_member(auth_user, old_membernumber, payload):

    try:
        db_member = (
                    Member.query
                    .filter(Member.membernumber == old_membernumber)
                    .one()
                )
    except NoResultFound:
        raise NotFound

    new_member_d = {
            'membernumber': str(payload['membernumber']),
            'established': db_member.established, # Wont change
            'firstname': str(payload['firstname']),
            'lastname': str(payload['lastname']),
            'address': str(payload['address']),
            'address2': str(payload['address2']),
            'city': str(payload['city']),
            'state': str(payload['state']),
            'zipcode': str(payload['zipcode']),
            'phone': str(payload['phone']),
            'email': str(payload['email']),
            'password': str(payload['password']),
            'question': str(payload['question']),
            'answer': str(payload['answer']),
            'activationcode': str(payload['activationcode']),
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

    db_member.membernumber = new_member_d['membernumber']
    db_member.established = new_member_d['established']
    db_member.firstname = new_member_d['firstname']
    db_member.lastname = new_member_d['lastname']
    db_member.address = new_member_d['address']
    db_member.address2 = new_member_d['address2']
    db_member.city = new_member_d['city']
    db_member.state = new_member_d['state']
    db_member.zipcode = new_member_d['zipcode']
    db_member.phone = new_member_d['phone']
    db_member.email = new_member_d['email']
    db_member.password = new_member_d['password']
    db_member.question = new_member_d['question']
    db_member.answer = new_member_d['answer']
    db_member.activationcode = new_member_d['activationcode']
    db_member.admin = new_member_d['admin']

    try:
        db.session.commit()

        db_member = (
                    Member.query
                    .filter(Member.membernumber == new_member_d['membernumber'])
                    .one()
                )
        app.logger.info("Replaced member {}: {} {}"
                .format(
                    db_member.membernumber,
                    db_member.firstname,
                    db_member.lastname,
                    )
                )

    except IntegrityError as e:
        app.logger.error("IntegrityError: {}".format(e))
        raise Forbidden("Unable to replace resource: IntegrityError")

    return db_member.as_api_dict()

def patch_member(auth_user, old_membernumber, payload):

    try:
        db_member = (
                    Member.query
                    .filter(Member.membernumber == new_member_d['membernumber'])
                    .one()
                )
    except NoResultFound:
        raise NotFound

    new_member_d = {
            'membernumber': str(payload.get('membernumber',
                db_member.membernumber)),
            'established': db_member.established, # Wont change
            'firstname': str(payload.get('firstname',
                db_member.firstname)),
            'lastname': str(payload.get('lastname',
                db_member.lastname)),
            'address': str(payload.get('address',
                db_member.address)),
            'address2': str(payload.get('address2',
                db_member.address2)),
            'city': str(payload.get('city',
                db_member.city)),
            'state': str(payload.get('state',
                db_member.state)),
            'zipcode': str(payload.get('zipcode',
                db_member.zipcode)),
            'phone': str(payload.get('phone',
                db_member.phone)),
            'email': str(payload.get('email',
                db_member.email)),
            'password': str(payload.get('password',
                db_member.password)),
            'question': str(payload.get('question',
                db_member.question)),
            'answer': str(payload.get('answer',
                db_member.answer)),
            'activationcode': str(payload.get('activationcode',
                db_member.activationcode)),
            'admin': str(payload.get('admin',
                db_member.admin)),
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

    db_member.membernumber = new_member_d['membernumber']
    db_member.established = new_member_d['established']
    db_member.firstname = new_member_d['firstname']
    db_member.lastname = new_member_d['lastname']
    db_member.address = new_member_d['address']
    db_member.address2 = new_member_d['address2']
    db_member.city = new_member_d['city']
    db_member.state = new_member_d['state']
    db_member.zipcode = new_member_d['zipcode']
    db_member.phone = new_member_d['phone']
    db_member.email = new_member_d['email']
    db_member.password = new_member_d['password']
    db_member.question = new_member_d['question']
    db_member.answer = new_member_d['answer']
    db_member.activationcode = new_member_d['activationcode']
    db_member.admin = new_member_d['admin']

    try:
        db.session.commit()

        db_member = (
                    Member.query
                    .filter(Member.membernumber == new_member_d['membernumber'])
                    .one()
                )
        app.logger.info("Patched member {}: {} {}"
                .format(
                    db_member.membernumber,
                    db_member.firstname,
                    db_member.lastname,
                    )
                )

    except IntegrityError as e:
        app.logger.error("IntegrityError: {}".format(e))
        raise Forbidden("Unable to patch member: IntegrityError")

    return db_member.as_api_dict()

def delete_member(auth_user, old_membernumber, payload):

    try:
        db_member = (
                    Member.query
                    .filter(Member.membernumber == old_membernumber)
                    .one()
                )
    except NoResultFound:
        raise NotFound

    try:
        db.session.delete(db_member)
        db.session.commit()

        app.logger.info("Deleted member %s" % old_membernumber)

    except IntegrityError as e:
        app.logger.error("IntegrityError: %s" % str(e))
        raise Forbidden("Unable to delete item: IntegrityError")

    return {'message': "Member %s successfully deleted by %s" % \
            (old_membernumber, auth_user)}


### Business logic for Item DAOs

def get_items(q_itemnumber=None, q_membernumber=None, q_description=None,
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

    pagination = db_item.paginate(page=page, per_page=per_page,
        error_out=False)
    items_l = pagination.items

    if app.config['LEGACY_UCS_ENABLED']:

        nullstring = lambda x: x if x else ''
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

        legacy_db = sql.connect(
                host=app.config['LEGACY_UCS_SQLHOST'],
                user=app.config['LEGACY_UCS_SQLUSER'],
                passwd=app.config['LEGACY_UCS_SQLPASS'],
                db=app.config['LEGACY_UCS_SQLDB']
                )

        legacy_db.c = legacy_db.cursor()
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

    return items_l

def create_item(payload):

    itemnumber = (int(Item.query.count()) + 1)

    new_item_d = {
            'itemnumber': str(itemnumber),
            'membernumber': str(payload['membernumber']),
            'description': str(payload['description']),
            'category': str(payload['category']),
            'subject': str(payload['subject']),
            'publisher': str(payload['publisher']),
            'year': str(payload['year']),
            'isbn': str(payload['isbn']),
            'condition': str(payload['condition']),
            'conditiondetail': str(payload['conditiondetail']),
            'numitems': str(payload['numitems']),
            'price': Decimal(str(payload['price'])) \
                    .quantize(Decimal(".01"), ROUND_HALF_UP),
            'discountprice': Decimal(str(payload['discountprice'])) \
                    .quantize(Decimal(".01"), ROUND_HALF_UP),
            'donate': str(payload['donate']),
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

        app.logger.info("Created item {}: {}"
                .format(
                    new_item.ID,
                    new_item.Description
                    )
                )

    except IntegrityError as e:
        app.logger.error("IntegrityError: {}".format(e))
        raise Forbidden("Unable to create resource: IntegrityError")

    return new_item

def replace_item(auth_user, old_itemnumber, payload):

    try:
        db_item = (
                    Item.query
                    .filter(Item.itemnumber == old_itemnumber)
                    .one()
                )
    except NoResultFound:
        raise NotFound

    new_item_d = {
            'itemnumber': str(db_item.itemnumber),
            'membernumber': str(payload['membernumber']),
            'description': str(payload['description']),
            'category': str(payload['category']),
            'subject': str(payload['subject']),
            'publisher': str(payload['publisher']),
            'year': str(payload['year']),
            'isbn': str(payload['isbn']),
            'condition': str(payload['condition']),
            'conditiondetail': str(payload['conditiondetail']),
            'numitems': str(payload['numitems']),
            'price': Decimal(str(payload['price'])) \
                    .quantize(Decimal(".01"), ROUND_HALF_UP),
            'discountprice': Decimal(str(payload['discountprice'])) \
                    .quantize(Decimal(".01"), ROUND_HALF_UP),
            'donate': str(payload['donate']),
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

    db_item.itemnumber = new_item_d['itemnumber'],
    db_item.membernumber = new_item_d['membernumber'],
    db_item.description = new_item_d['description'],
    db_item.category = new_item_d['category'],
    db_item.subject = new_item_d['subject'],
    db_item.publisher = new_item_d['publisher'],
    db_item.year = new_item_d['year'],
    db_item.isbn = new_item_d['isbn'],
    db_item.condition = new_item_d['condition'],
    db_item.conditiondetail = new_item_d['conditiondetail'],
    db_item.numitems = new_item_d['numitems'],
    db_item.price = new_item_d['price'],
    db_item.discountprice = new_item_d['discountprice'],
    db_item.donate = new_item_d['donate'],

    try:
        db.session.commit()

        db_item = (
                Item.query
                    .filter(Item.MemberNumber == payload['MemberNumber'])
                    .filter(Item.ItemNumber == itemnumber)
                    .one()
                )

        app.logger.info("Replaced item {}: {}"
                .format(
                    new_item.ID,
                    new_item.Description
                    )
                )

    except IntegrityError as e:
        app.logger.error("IntegrityError: {}".format(e))
        raise Forbidden("Unable to replace item: IntegrityError")

    return db_item.as_api_dict()

def patch_item(auth_user, old_itemnumber, payload):

    try:
        db_item = (
                    Item.query
                    .filter(Item.itemnumber == old_itemnumber)
                    .one()
                )
    except NoResultFound:
        raise NotFound

    new_item_d = {
            'itemnumber': str(db_item.itemnumber),
            'membernumber': str(payload.get('membernumber',
                db_item.membernumber)),
            'description': str(payload.get('description',
                db_item.description)),
            'category': str(payload.get('category',
                db_item.category)),
            'subject': str(payload.get('subject',
                db_item.subject)),
            'publisher': str(payload.get('publisher',
                db_item.publisher)),
            'year': str(payload.get('year',
                db_item.year)),
            'isbn': str(payload.get('isbn',
                db_item.isbn)),
            'condition': str(payload.get('condition',
                db_item.condition)),
            'conditiondetail': str(payload.get('conditiondetail',
                db_item.conditiondetail)),
            'numitems': str(payload.get('numitems',
                db_item.numitems)),
            'price': Decimal(
                str(payload.get('price', db_item.price)) \
                    .quantize(Decimal(".01")),
                ROUND_HALF_UP
                ),
            'discountprice': Decimal(
                str(payload.get('discountprice', db_item.discountprice)) \
                    .quantize(Decimal(".01")),
                ROUND_HALF_UP
                ),
            'donate': str(payload.get('donate',
                db_item.donate)),
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

    db_item.itemnumber = new_item_d['itemnumber'],
    db_item.membernumber = new_item_d['membernumber'],
    db_item.description = new_item_d['description'],
    db_item.category = new_item_d['category'],
    db_item.subject = new_item_d['subject'],
    db_item.publisher = new_item_d['publisher'],
    db_item.year = new_item_d['year'],
    db_item.isbn = new_item_d['isbn'],
    db_item.condition = new_item_d['condition'],
    db_item.conditiondetail = new_item_d['conditiondetail'],
    db_item.numitems = new_item_d['numitems'],
    db_item.price = new_item_d['price'],
    db_item.discountprice = new_item_d['discountprice'],
    db_item.donate = new_item_d['donate'],

    try:
        db.session.commit()

        db_item = (
                Item.query
                    .filter(Item.MemberNumber == payload['MemberNumber'])
                    .filter(Item.ItemNumber == itemnumber)
                    .one()
                )

        app.logger.info("Patched item {}: {}"
                .format(
                    new_item.ID,
                    new_item.Description
                    )
                )

    except IntegrityError as e:
        app.logger.error("IntegrityError: {}".format(e))
        raise Forbidden("Unable to patch item: IntegrityError")

    return db_item.as_api_dict()

def delete_item(auth_user, old_itemnumber, payload):

    try:
        db_item = (
                    Item.query
                    .filter(Item.itemnumber == old_itemnumber)
                    .one()
                )
    except NoResultFound:
        raise NotFound

    db_item.deleted = '1'

    try:
        #db.session.delete(db_item)
        db.session.commit()

        app.logger.info("Deleted item %s" % old_itemnumber)

    except IntegrityError as e:
        app.logger.error("IntegrityError: %s" % str(e))
        raise Forbidden("Unable to delete item: IntegrityError")

    return {'message': "Item %s successfully deleted by %s" % \
            (old_itemnumber, auth_user)}


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

    pagination = db_transaction.paginate(page=page, per_page=per_page,
        error_out=False)
    transactions_l = pagination.items
    if app.config['LEGACY_UCS_ENABLED']:

        nullstring = lambda x: x if x else ''
        formatprice = lambda x: str(Decimal(x).quantize(Decimal('0.01'),
            rounding=ROUND_HALF_UP))

        legacy_db = sql.connect(
                host=app.config['LEGACY_UCS_SQLHOST'],
                user=app.config['LEGACY_UCS_SQLUSER'],
                passwd=app.config['LEGACY_UCS_SQLPASS'],
                db=app.config['LEGACY_UCS_SQLDB']
                )

        legacy_db.c = legacy_db.cursor()
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

            transaction = {
                'uuid': str(i[0]),
                'datetime': str(i[1]),
                'user_username': i[2],
                'finalized': i[3],
                'payment_method': i[4],
                'total': str(i[7]),
                }
            transactions_l.append(transaction)

    return transactions_l


### Business logic for User DAOs

def get_users(q_username=None, q_firstname=None, q_lastname=None,
        page=1, per_page=25):

    page = page if page else 1
    per_page = per_page if per_page else 25

    db_user = (
            db.session.query(User)
            .order_by(User.username.asc())
        )
    if q_username:
        db_user = db_user.filter(User.username.like("{}%%"
                .format(q_username)))
    if q_firstname:
        db_user = db_user.filter(User.firstname.like("{}%%"
                .format(q_firstname)))
    if q_lastname:
        db_user = db_user.filter(User.lastname.like("{}%%"
                .format(q_lastname)))

    pagination = db_user.paginate(page=page, per_page=per_page,
            error_out=False)
    users_l = pagination.items

    return users_l

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

    except IntegrityError as e:
        app.logger.error("IntegrityError: %s" % str(e))
        raise Forbidden("Unable to create resource: IntegrityError")

    return db_user

def replace_user(auth_user, old_username, payload):

    try:
        db_user = User.query.filter(User.username == old_username).one()
    except:
        raise NotFound

    new_user = {
            'username': str(payload['username']),
            'password': generate_password_hash(str(payload['password']),
                app.config['PW_HASH']),
            'firstname': str(payload['firstname']),
            'lastname': str(payload['lastname']),
            }

    db_user.username = new_user.get('username',db_user.username)
    db_user.password = new_user.get('password',db_user.password)
    db_user.firstname = new_user.get('firstname',db_user.firstname)
    db_user.lastname = new_user.get('lastname',db_user.lastname)
   
    try:
        db.session.commit()

        db_user = User.query.filter(User.username == new_user['username']).one()

        app.logger.info("Replaced user %s with %s" % \
                (old_username, db_user.username))

    except IntegrityError as e:
        app.logger.error("IntegrityError: %s" % str(e))
        raise Forbidden("Unable to replace resource: IntegrityError")

    return db_user

def patch_user(auth_user, old_username, payload):

    try:
        db_user = User.query.filter(User.username == old_username).one()
    except:
        raise NotFound

    new_user = {
            'username': str(payload.get('username', db_user.username)),
            'password': str(payload.get('password', db_user.password)),
            'firstname': str(payload.get('firstname', db_user.firstname)),
            'lastname': str(payload.get('lastname', db_user.lastname)),
            }

    if 'password' in payload:
        new_user['password'] = generate_password_hash(str(payload['password']),
                app.config['PW_HASH']),

    db_user.username = new_user.get('username',db_user.username)
    db_user.password = new_user.get('password',db_user.password)
    db_user.firstname = new_user.get('firstname',db_user.firstname)
    db_user.lastname = new_user.get('lastname',db_user.lastname)

    try:
        db.session.commit()

        db_user = User.query.filter(User.username == new_user['username']).one()

        app.logger.info("Patched user %s with %s" % \
                (old_username, db_user.username))

    except IntegrityError as e:
        app.logger.error("IntegrityError: %s" % str(e))
        raise Forbidden("Unable to patch resource: IntegrityError")

    return db_user

def delete_user(auth_user, old_username, payload):

    try:
        db_user = User.query.filter(User.username == old_username).one()
    except:
        raise NotFound

    try:
        db.session.delete(db_user)
        db.session.commit()

        app.logger.info("Deleted user %s" % old_username)

    except IntegrityError as e:
        app.logger.error("IntegrityError: %s" % str(e))
        raise Forbidden("Unable to delete resource: IntegrityError")

    return {'message': "User %s successfully deleted by %s" % \
            (old_username, auth_user)}


### Business logic for Barcode DAOs

def generate_barcode(codedata):

    if app.config['BARCODE_SYMBOLOGY'] in barcode.PROVIDED_BARCODES:

        app.logger.info("Generating barcode for {}".format(codedata))

        imgstore = {}
        imgstore['MEM'] = BytesIO()
        imgstore['FILE'] = "{}/{}".format(
                app.config['BARCODE_TEMPDIR'],
                codedata
                )

        barcode_img = imgstore[app.config['BARCODE_STORAGE']]
        barcode.generate(
            app.config['BARCODE_SYMBOLOGY'],
            codedata,
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
