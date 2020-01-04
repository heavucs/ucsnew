import datetime
import re
import uuid
import barcode
from io import BytesIO
import MySQLdb as sql
from decimal import Decimal, ROUND_HALF_UP

from flask import current_app

from .models import db
from .models import Member
from .models import Item
from .models import Transaction
from .models import Transaction_item
from .models import User
from .models import AuditLog
from .models import AuditLogTag

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from werkzeug.exceptions import BadRequest      # 400
from werkzeug.exceptions import Unauthorized    # 401
from werkzeug.exceptions import Forbidden       # 403
from werkzeug.exceptions import NotFound        # 404
from werkzeug.security import generate_password_hash

app = current_app


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

def create_member(auth_user, payload):

    log_tags = {}

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
            'password': generate_password_hash(str(payload['password']),
                app.config['PW_HASH']),
            'question': str(payload['question']),
            'answer': str(payload['answer']),
            'activationcode': str(payload['activationcode']),
            'admin': str(payload['admin']),
            }

    db_member = Member(
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
        db.session.add(db_member)
        db.session.commit()

        new_member_d = db_member.as_api_dict()
        log_tags[new_member_d['membernumber']] = 'membernumber'

        app.logger.info("Created member {}: {} {}"
                .format(
                    new_member_d['membernumber'],
                    new_member_d['firstname'],
                    new_member_d['lastname'],
                    )
                )

    except IntegrityError as e:
        app.logger.error("IntegrityError: {}".format(e))
        raise Forbidden("Unable to create member: IntegrityError")

    create_auditlog(auth_user, {
            'text': "Created member {}: {} {}".format(
                new_member_d['membernumber'],
                new_member_d['firstname'],
                new_member_d['lastname'],
                ),
            'tags': log_tags,
            }
        )

    return new_member_d

def replace_member(auth_user, old_membernumber, payload):

    log_tags = {}

    try:
        db_member = (
                    Member.query
                    .filter(Member.membernumber == old_membernumber)
                    .one()
                )
    except NoResultFound:
        raise NotFound

    log_tags[old_membernumber] = 'membernumber'

    new_member_d = {
            'membernumber': db_member.membernumber, # Wont change
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
            'password': generate_password_hash(str(payload['password']),
                app.config['PW_HASH']),
            'question': str(payload['question']),
            'answer': str(payload['answer']),
            'activationcode': str(payload['activationcode']),
            'admin': str(payload['admin']),
            }

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

        new_member_d = db_member.as_api_dict()

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

    create_auditlog(auth_user, {
            'text': "Replaced member {}: {} {}".format(
                new_member_d['membernumber'],
                new_member_d['firstname'],
                new_member_d['lastname'],
                ),
            'tags': log_tags,
            }
        )

    return new_member_d

def patch_member(auth_user, old_membernumber, payload):

    log_tags = {}

    try:
        db_member = (
                    Member.query
                    .filter(Member.membernumber == old_membernumber)
                    .one()
                )
    except NoResultFound:
        raise NotFound

    log_tags[old_membernumber] = 'membernumber'

    new_member_d = {
            'membernumber': db_member.membernumber, # Wont change
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

    if 'password' in payload:
        new_member_d['password'] = generate_password_hash(
                str(payload['password']),
                app.config['PW_HASH'],
                ),

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

        new_member_d = db_member.as_api_dict()

        app.logger.info("Patched member {}: {} {}"
                .format(
                    new_member_d['membernumber'],
                    new_member_d['firstname'],
                    new_member_d['lastname'],
                    )
                )

    except IntegrityError as e:
        app.logger.error("IntegrityError: {}".format(e))
        raise Forbidden("Unable to patch member: IntegrityError")

    create_auditlog(auth_user, {
            'text': "Patched member {}: {} {}".format(
                new_member_d['membernumber'],
                new_member_d['firstname'],
                new_member_d['lastname'],
                ),
            'tags': log_tags,
            }
        )

    return new_member_d

def delete_member(auth_user, old_membernumber, payload):

    log_tags = {}

    try:
        db_member = (
                    Member.query
                    .filter(Member.membernumber == old_membernumber)
                    .one()
                )
    except NoResultFound:
        raise NotFound

    log_tags[old_membernumber] = 'membernumber'
    new_member_d = db_member.as_api_dict()

    try:
        db.session.delete(db_member)
        db.session.commit()

        app.logger.info("Deleted member {}: {} {}"
                .format(
                    new_member_d['membernumber'],
                    new_member_d['firstname'],
                    new_member_d['lastname'],
                    )
                )

    except IntegrityError as e:
        app.logger.error("IntegrityError: {}".format(str(e)))
        raise Forbidden("Unable to delete item: IntegrityError")

    create_auditlog(auth_user, {
            'text': "Deleted member {}: {} {}".format(
                new_member_d['membernumber'],
                new_member_d['firstname'],
                new_member_d['lastname'],
                ),
            'tags': log_tags,
            }
        )

    return new_member_d

def listitemfrom_member(old_membernumber):

    try:
        db_member = (
                    Member.query
                    .filter(Member.membernumber == old_membernumber)
                    .one()
                )
    except NoResultFound:
        raise NotFound

    return get_items(q_membernumber=old_membernumber)


### Business logic for Item DAOs

def get_items(q_item_uuid=None, q_membernumber=None, q_description=None,
        q_transaction_uuid=None, page=1, per_page=25):

    page = page if page else 1
    per_page = per_page if per_page else 25

    db_item = (
                db.session.query(Item)
                .order_by(Item.uuid.asc())
            )
    if q_item_uuid:
        db_item = db_item.filter(Item.uuid.like("{}%%"
                .format(q_item_uuid)))
    if q_membernumber:
        db_item = db_item.filter(Item.member_membernumber.like("{}%%"
                .format(q_membernumber)))
    if q_description:
        db_item = db_item.filter(Item.description.like("%%{}%%"
                .format(q_description)))
    if q_transaction_uuid:
        db_item = db_item.join(Transaction_item)
        db_item = db_item.join(Transaction)
        db_item = db_item.filter(Transaction.uuid == q_transaction_uuid)

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
                        "WHERE ID like \"{}%%\""
                            .format(nullstring(q_item_uuid)),
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
                'uuid': i[0],
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

def create_item(auth_user, payload):

    log_tags = {}

    db_item = (
                db.session.query(Item)
                .filter_by(member_membernumber=payload['membernumber'])
                .order_by(Item.uuid.asc())
            )
    itemnumber = (int(db_item.count()) + 1)

    new_item_d = {
            'uuid': str(uuid.uuid4()),
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

    db_item = Item(
            new_item_d['uuid'],
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
        db.session.add(db_item)
        db.session.commit()

        new_item_d = db_item.as_api_dict()
        log_tags[new_item_d['uuid']] = 'item_uuid'

        app.logger.info("Created item {}: {}"
                .format(
                    new_item_d['uuid'],
                    new_item_d['description'],
                    )
                )

    except IntegrityError as e:
        app.logger.error("IntegrityError: {}".format(e))
        raise Forbidden("Unable to create resource: IntegrityError")

    create_auditlog(auth_user, {
            'text': "Created item {}: {}".format(
                new_item_d['uuid'],
                new_item_d['description'],
                ),
            'tags': log_tags,
            }
        )

    return new_item_d

def replace_item(auth_user, old_uuid, payload):

    log_tags = {}

    try:
        db_item = (
                    Item.query
                    .filter(Item.uuid == old_uuid)
                    .one()
                )
    except NoResultFound:
        raise NotFound

    log_tags[old_uuid] = 'item_uuid'

    new_item_d = {
            'itemnumber': db_item.itemnumber,       # Wont change
            'membernumber': db_item.membernumber,   # Wont change
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

        new_item_d = db_item.as_api_dict()

        app.logger.info("Replaced item {}: {}"
                .format(
                    new_item_d['uuid'],
                    new_item_d['description'],
                    )
                )

    except IntegrityError as e:
        app.logger.error("IntegrityError: {}".format(e))
        raise Forbidden("Unable to replace item: IntegrityError")

    create_auditlog(auth_user, {
            'text': "Replaced item {}: {}".format(
                new_item_d['uuid'],
                new_item_d['description'],
                ),
            'tags': log_tags,
            }
        )

    return new_item_d

def patch_item(auth_user, old_uuid, payload):

    log_tags = {}

    try:
        db_item = (
                    Item.query
                    .filter(Item.uuid == old_uuid)
                    .one()
                )
    except NoResultFound:
        raise NotFound("This is a not found error ")

    log_tags[old_uuid] = 'item_uuid'

    new_item_d = {
            'itemnumber': db_item.itemnumber,       # Wont change
            'membernumber': db_item.membernumber,   # Wont change
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
                str(payload.get('price', db_item.price))
                ).quantize(Decimal(".01"), ROUND_HALF_UP),
            'discountprice': Decimal(
                str(payload.get('discountprice', db_item.discountprice))
                ).quantize(Decimal(".01"), ROUND_HALF_UP),
            'donate': str(payload.get('donate',
                db_item.donate)),
            }

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

        new_item_d = db_item.as_api_dict()

        app.logger.info("Patched item {}: {}"
                .format(
                    new_item_d['uuid'],
                    new_item_d['description'],
                    )
                )

    except IntegrityError as e:
        app.logger.error("IntegrityError: {}".format(e))
        raise Forbidden("Unable to patch item: IntegrityError")

    create_auditlog(auth_user, {
            'text': "Patched item {}: {}".format(
                new_item_d['uuid'],
                new_item_d['description'],
                ),
            'tags': log_tags,
            }
        )

    return new_item_d

def delete_item(auth_user, old_itemnumber, payload):

    log_tags = {}

    try:
        db_item = (
                    Item.query
                    .filter(Item.itemnumber == old_itemnumber)
                    .one()
                )
    except NoResultFound:
        raise NotFound

    log_tags[old_uuid] = 'item_uuid'
    new_item_d = db_item.as_api_dict()

    db_item.deleted = '1'

    try:
        #db.session.delete(db_item)
        db.session.commit()

        app.logger.info("Deleted item {}: {}"
                .format(
                    new_item_d['uuid'],
                    new_item_d['description'],
                    )
                )

    except IntegrityError as e:
        app.logger.error("IntegrityError: {}".format(str(e)))
        raise Forbidden("Unable to delete item: IntegrityError")

    create_auditlog(auth_user, {
            'text': "Deleted item {}: {}".format(
                new_item_d['uuid'],
                new_item_d['description'],
                ),
            'tags': log_tags,
            }
        )

    return new_item_d


### Business logic for Transaction DAOs

def get_transactions(q_username=None, q_itemnumber=None, q_transaction_uuid=None,
        q_finalized=None, page=1, per_page=25):

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
    if q_transaction_uuid:
        db_transaction = db_transaction.filter(Transaction.uuid.like("%%{}%%"
                .format(q_transaction_uuid)))
    if q_finalized:
        if isinstance(q_finalized, str):
            if finalized == 'True' or finalized == '1':
                finalized = True
            else:
                finalized = False
        db_transaction = db_transaction.filter(Transaction.finalized == finalized)

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
                                .format(nullstring(q_transaction_uuid)),
                            (page * per_page - per_page),
                            per_page,
                            )
                        )
        legacy_transactions_l = legacy_db.c.fetchall()

        for i in legacy_transactions_l:

            transaction = {
                'uuid': str(i[0]),
                'ctime': str(i[1]),
                'user_username': i[2],
                'finalized': i[3],
                'payment_method': i[4],
                'total': str(i[7]),
                }
            transactions_l.append(transaction)

    return transactions_l

def create_transaction(auth_user, payload):

    log_tags = {}

    previous = get_transactions(q_username=auth_user, q_finalized=False)
    if len(previous) > 0:
        previous = previous[0]
        raise BadRequest("Transaction {} already open by {}".format(
            previous.uuid, auth_user))

    new_transaction_d = {
            'user': auth_user,
            'finalized': False,
            'ftime': None,
            'payment_method': "0",
            'payment_note': "",
            'total': Decimal(0),
            }

    db_transaction = Transaction(
            new_transaction_d['user'],
            new_transaction_d['finalized'],
            new_transaction_d['ftime'],
            new_transaction_d['payment_method'],
            new_transaction_d['payment_note'],
            new_transaction_d['total'],
            )

    try:
        db.session.add(db_transaction)
        db.session.commit()

        new_transaction_d = db_transaction.as_api_dict()
        log_tags[new_transaction_d['uuid']] = 'transaction_uuid'

        app.logger.info("Created transaction {}"
                .format(
                    db_transaction.uuid,
                    )
                )

    except IntegrityError as e:
        app.logger.error("IntegrityError: {}".format(e))
        raise Forbidden("Unable to create transaction: IntegrityError")

    create_auditlog(auth_user, {
            'text': "Created transaction {}".format(
                new_transaction_d['uuid'],
                ),
            'tags': log_tags,
            }
        )

    return db_transaction.as_api_dict()

def replace_transaction(auth_user, old_transaction_uuid, payload):

    log_tags = {}

    try:
        db_transaction = (
                    Transaction.query
                    .filter(Transaction.uuid == old_transaction_uuid)
                    .one()
                )
    except NoResultFound:
        raise NotFound

    log_tags[old_transaction_uuid] = 'transaction_uuid'

    finalized = payload['finalized']
    if isinstance(finalized, str):
        if finalized == 'True' or finalized == '1':
            finalized = True
        else:
            finalized = False

    if (db_transaction.finalized == True
            and finalized == True):
        raise BadRequest("Transaction {} is already finalized".format(
            old_transaction_uuid))

    if (db_transaction.finzalized == False
            and finalized == True):
        db_transaction.ftime = datetime.datetime.now()

        create_auditlog(auth_user, {
                'text': "Transaction {} is being finalized".format(
                    new_transaction_d['uuid'],
                    ),
                'tags': log_tags,
                }
            )

    if (db_transaction.finalized == True
            and finalized == False):

        create_auditlog(auth_user, {
                'text': "Transaction {} is being reopened".format(
                    new_transaction_d['uuid'],
                    ),
                'tags': log_tags,
                }
            )

    new_transaction_d = {
            'finalized': finalized,
            'ftime': db_transaction.ftime,
            'payment_method': str(payload['payment_method']),
            'total': str(payload['total']),
            }

    db_transaction.finalized = new_transaction_d['finalized']
    db_transaction.ftime = new_transaction_d['ftime']
    db_transaction.payment_method = new_transaction_d['payment_method']
    db_transaction.total = new_transaction_d['total']

    try:
        db.session.commit()

        new_transaction_d = db_transaction.as_api_dict()

        app.logger.info("Replaced transaction {}"
                .format(
                    new_transaction_d['uuid'],
                    )
                )

    except IntegrityError as e:
        app.logger.error("IntegrityError: {}".format(e))
        raise Forbidden("Unable to replace item: IntegrityError")

    create_auditlog(auth_user, {
            'text': "Replaced transaction {}".format(
                new_transaction_d['uuid'],
                ),
            'tags': log_tags,
            }
        )

    return new_transaction_d

def patch_transaction(auth_user, old_transaction_uuid, payload):

    log_tags = {}

    try:
        db_transaction = (
                    Transaction.query
                    .filter(Transaction.uuid == old_transaction_uuid)
                    .one()
                )
    except NoResultFound:
        raise NotFound

    log_tags[old_transaction_uuid] = 'transaction_uuid'

    finalized = payload.get('finalized', db_transaction.finalized)
    if isinstance(finalized, str):
        if finalized == 'True' or finalized == '1':
            finalized = True
        else:
            finalized = False

    if (db_transaction.finalized == True
            and finalized == True):
        raise BadRequest("Transaction {} is already finalized".format(
            old_transaction_uuid))

    if (db_transaction.finalized == False
            and finalized == True):
        db_transaction.ftime = datetime.datetime.now()

        create_auditlog(auth_user, {
                'text': "Transaction {} is being finalized".format(
                    new_transaction_d['uuid'],
                    ),
                'tags': log_tags,
                }
            )

    if (db_transaction.finalized == True
            and finalized == False):

        create_auditlog(auth_user, {
                'text': "Transaction {} is being reopened".format(
                    new_transaction_d['uuid'],
                    ),
                'tags': log_tags,
                }
            )

    new_transaction_d = {
            'finalized': finalized,
            'ftime': db_transaction.ftime,
            'payment_method': str(payload.get('payment_method',
                db_transaction.payment_method)),
            'total': str(payload.get('total',
                db_transaction.total)),
            }

    db_transaction.finalized = new_transaction_d['finalized']
    db_transaction.ftime = new_transaction_d['ftime']
    db_transaction.payment_method = new_transaction_d['payment_method']
    db_transaction.total = new_transaction_d['total']

    try:
        db.session.commit()

        new_transaction_d = db_transaction.as_api_dict()

        app.logger.info("Patched transaction {}"
                .format(
                    new_transaction_d['uuid'],
                    )
                )

    except IntegrityError as e:
        app.logger.error("IntegrityError: {}".format(e))
        raise Forbidden("Unable to patch item: IntegrityError")

    create_auditlog(auth_user, {
            'text': "Patched transaction {}".format(
                new_transaction_d['uuid'],
                ),
            'tags': log_tags,
            }
        )

    return new_transaction_d

def delete_transaction(auth_user, old_transaction_uuid, payload):

    log_tags = {}

    try:
        db_transaction = (
                    Transaction.query
                    .filter(Transaction.uuid == old_transaction_uuid)
                    .one()
                )
    except NoResultFound:
        raise NotFound

    log_tags[old_transaction_uuid] = 'transaction_uuid'
    new_transaction_d = db_transaction.as_api_dict()

    if db_transaction.finalized == True:
        raise BadRequest("Transaction {} is already finalized".format(
            old_transaction_uuid))

    num_items = len(listitemfrom_transaction(old_transaction_uuid))
    if num_items > 0:
        raise BadRequest("Unable to delete transaction {} with items {}".format(
            old_transaction_uuid, num_items))

    try:
        db.session.delete(db_transaction)
        db.session.commit()

        app.logger.info("Deleted transaction {}".format(old_transaction_uuid))

    except IntegrityError as e:
        app.logger.error("IntegrityError: {}".format(str(e)))
        raise Forbidden("Unable to delete item: IntegrityError")

    create_auditlog(auth_user, {
            'text': "Deleted transaction {}".format(
                new_transaction_d['uuid'],
                ),
            'tags': log_tags,
            }
        )

    return new_transaction_d

def listitemfrom_transaction(old_transaction_uuid):

    try:
        db_transaction = (
                    Transaction.query
                    .filter(Transaction.uuid == old_transaction_uuid)
                    .one()
                )
    except NoResultFound:
        raise NotFound

    return get_items(q_transaction_uuid=old_transaction_uuid)

def additemto_transaction(auth_user, old_transaction_uuid, old_item_uuid):

    log_tags = {}

    try:
        db_transaction = (
                    Transaction.query
                    .filter(Transaction.uuid == old_transaction_uuid)
                    .one()
                )
    except NoResultFound:
        raise NotFound

    log_tags[old_transaction_uuid] = 'transaction_uuid'

    if db_transaction.finalized == True:
        raise BadRequest("Transaction {} is already finalized".format(
            old_transaction_uuid))

    try:
        db_item = (
                    Item.query
                    .filter(Item.uuid == old_item_uuid)
                    .one()
                )
    except NoResultFound:
        raise NotFound

    log_tags[old_item_uuid] = 'item_uuid'

    if db_transaction.finalized:
        raise BadRequest("Transaction {} is finalized".format(
            old_transaction_uuid))

    try:
        db_transaction.items.append(db_item)
        db.session.commit()

        app.logger.info("Added item {}({}) to transaction {}".format(
            db_item.description, old_item_uuid, old_transaction_uuid))

    except IntegrityError as e:
        app.logger.error("IntegrityError: {}".format(str(e)))
        raise Forbidden("Unable to add item to transaction: IntegrityError")

    create_auditlog(auth_user, {
            'text': "Added item {}({}) to transaction {}".format(
                db_item.description,
                old_item_uuid,
                old_transaction_uuid,
                ),
            'tags': log_tags,
            }
        )

    return listitemfrom_transaction(old_transaction_uuid)

def removeitemfrom_transaction(auth_user, old_transaction_uuid, old_item_uuid):

    log_tags = {}

    try:
        db_transaction = (
                    Transaction.query
                    .filter(Transaction.uuid == old_transaction_uuid)
                    .one()
                )
    except NoResultFound:
        raise NotFound

    log_tags[old_transaction_uuid] = 'transaction_uuid'

    if db_transaction.finalized == True:
        raise BadRequest("Transaction {} is already finalized".format(
            old_transaction_uuid))

    try:
        db_item = (
                    Item.query
                    .filter(Item.uuid == old_item_uuid)
                    .one()
                )
    except NoResultFound:
        raise NotFound

    log_tags[old_item_uuid] = 'item_uuid'

    if db_transaction.finalized:
        raise BadRequest("Transaction {} is finalized".format(
            old_transaction_uuid))

    try:
        db_transaction.items.remove(db_item)
        db.session.commit()

        app.logger.info("Removed item {}({}) from transaction {}".format(
            db_item.description, old_item_uuid, old_transaction_uuid))

    except IntegrityError as e:
        app.logger.error("IntegrityError: {}".format(str(e)))
        raise Forbidden("Unable to remove item from transaction: IntegrityError")

    create_auditlog(auth_user, {
            'text': "Removed item {}({}) to transaction {}".format(
                db_item.description,
                old_item_uuid,
                old_transaction_uuid,
                ),
            'tags': log_tags,
            }
        )

    return listitemfrom_transaction(old_transaction_uuid)


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

def create_user(auth_user, payload):

    log_tags = {}

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

        new_user_d = db_user.as_api_dict()
        log_tags[new_user_d['uuid']] = 'username'

        app.logger.info("Created user {}".format(new_user_d['username']))

    except IntegrityError as e:
        app.logger.error("IntegrityError: {}".format(str(e)))
        raise Forbidden("Unable to create resource: IntegrityError")

    create_auditlog(auth_user, {
            'text': "Created user {}".format(
                new_user_d['username'],
                ),
            'tags': log_tags,
            }
        )

    return new_user_d

def replace_user(auth_user, old_username, payload):

    log_tags = {}

    try:
        db_user = User.query.filter(User.username == old_username).one()
    except:
        raise NotFound

    log_tags[old_username] = 'username'
    if not old_username == payload['username']:
        log_tags[payload['username']] = 'username'

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

        new_user_d = db_user.as_api_dict()
        log_tags[new_user_d['uuid']] = 'user_uuid'

        app.logger.info("Replaced user {} with {}".format(
            old_username, new_user_d['username']))

    except IntegrityError as e:
        app.logger.error("IntegrityError: {}".format(str(e)))
        raise Forbidden("Unable to replace resource: IntegrityError")

    create_auditlog(auth_user, {
            'text': "Replaced user {} with {}".format(
                old_username,
                new_user_d['username'],
                ),
            'tags': log_tags,
            }
        )

    return new_user_d

def patch_user(auth_user, old_username, payload):

    log_tags = {}

    try:
        db_user = User.query.filter(User.username == old_username).one()
    except:
        raise NotFound

    log_tags[old_username] = 'username'
    if not old_username == payload.get('username', ''):
        log_tags[payload['username']] = 'username'

    new_user_d = {
            'username': str(payload.get('username', db_user.username)),
            'password': str(payload.get('password', db_user.password)),
            'firstname': str(payload.get('firstname', db_user.firstname)),
            'lastname': str(payload.get('lastname', db_user.lastname)),
            }

    if 'password' in payload:
        new_user_d['password'] = generate_password_hash(
                str(payload['password']),
                app.config['PW_HASH'],
                ),

    db_user.username = new_user_d.get('username',db_user.username)
    db_user.password = new_user_d.get('password',db_user.password)
    db_user.firstname = new_user_d.get('firstname',db_user.firstname)
    db_user.lastname = new_user_d.get('lastname',db_user.lastname)

    try:
        db.session.commit()

        new_user_d = db_user.as_api_dict()

        app.logger.info("Patched user {} with {}".format(
            old_username, new_user_d['username']))

    except IntegrityError as e:
        app.logger.error("IntegrityError: {}".format(str(e)))
        raise Forbidden("Unable to patch resource: IntegrityError")

    create_auditlog(auth_user, {
            'text': "Patched user {} with {}".format(
                old_username,
                new_user_d['username'],
                ),
            'tags': log_tags,
            }
        )

    return new_user_d

def delete_user(auth_user, old_username, payload):

    log_tags = {}

    try:
        db_user = User.query.filter(User.username == old_username).one()
    except:
        raise NotFound

    log_tags[old_username] = 'username'
    new_user_d = db_user.as_api_dict()

    try:
        db.session.delete(db_user)
        db.session.commit()

        app.logger.info("Deleted user {}".format(old_username))

    except IntegrityError as e:
        app.logger.error("IntegrityError: {}".format(str(e)))
        raise Forbidden("Unable to delete resource: IntegrityError")

    create_auditlog(auth_user, {
            'text': "Deleted user {}".format(
                new_user_d['username'],
                ),
            'tags': log_tags,
            }
        )

    return new_user_d


def listtransactionfrom_user(old_username):

    try:
        db_user = (
                    User.query
                    .filter(User.username == old_username)
                    .one()
                )
    except NoResultFound:
        raise NotFound

    return get_transactions(q_username=old_username)


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

### Business logic for AuditLog DAOs

def get_auditlogs(q_auditlog_uuid=None, q_username=None, q_tag=None,
        page=1, per_page=25):

    page = page if page else 1
    per_page = per_page if per_page else 25

    db_auditlog = (
            db.session.query(AuditLog)
            .order_by(AuditLog.ctime.asc())
        )
    if q_auditlog_uuid:
        db_auditlog = db_auditlog.filter(AuditLog.uuid == q_auditlog_uuid)
    if q_username:
        db_auditlog = db_auditlog.filter(AuditLog.user.like("{}%%"
                .format(q_username)))
    if q_tag:
        db_auditlog = db_auditlog.join(AuditLogTag)
        db_auditlog = db_auditlog.filter(AuditLogTag.tag.like("{}%%"
                .format(q_tag)))

    pagination = db_auditlog.paginate(page=page, per_page=per_page,
            error_out=False)
    logs_l = pagination.items

    newlog_l = []
    for log in logs_l:
        new_log = log.as_api_dict().copy()

        tags = []
        for tag in get_auditlogtags(new_log['uuid']):
            tags.append(tag.as_api_dict()['tag'])
        new_log['tags'] = tags

        newlog_l.append(new_log)
    logs_l = newlog_l

    return logs_l

def create_auditlog(auth_user, payload):

    new_log_d = {
            'user': auth_user,
            'text': payload['text'],
            }

    if not new_log_d['text']:
        raise BadRequest("Unable to create blank log entry")

    db_auditlog = AuditLog(
            new_log_d['user'],
            new_log_d['text'],
            )

    try:
        db.session.add(db_auditlog)
        db.session.commit()

        new_log_d = db_auditlog.as_api_dict()

    except IntegrityError as e:
        app.logger.error("IntegrityError: {}".format(e))
        raise Forbidden("Unable to create log: IntegrityError")

    tags = payload.get('tags', {}).items()
    for tag, tagtype in tags:
        payload = {
                'tag': tag,
                'tagtype': tagtype,
                }
        create_auditlogtag(new_log_d['uuid'], payload)

    return new_log_d

def get_auditlogtags(q_auditlog_uuid=None):

    db_auditlogtag = (
            db.session.query(AuditLogTag)
            .order_by(AuditLogTag.ctime.asc())
        )
    if q_auditlog_uuid:
        db_auditlogtag = db_auditlogtag.join(AuditLog)
        db_auditlogtag = db_auditlogtag.filter(AuditLog.uuid == q_auditlog_uuid)

    tags_l = db_auditlogtag.all()

    return tags_l

def create_auditlogtag(auditlog_uuid, payload):

    try:
        db_auditlog = (
                AuditLog.query
                .filter(AuditLog.uuid == auditlog_uuid)
                .one()
            )
    except:
        raise NotFound

    new_tag_d = {
            'auditlog': db_auditlog,
            'tag': payload['tag'],
            'tagtype': payload.get('tagtype', ''),
            }

    if not new_tag_d['tag']:
        raise BadRequest("Unable to create blank log tag")


    db_auditlogtag = AuditLogTag(
            auditlog_uuid,
            new_tag_d['tag'],
            new_tag_d['tagtype'],
            )

    try:
        db.session.add(db_auditlogtag)
        db.session.commit()

        new_tag_d = db_auditlogtag.as_api_dict()

    except IntegrityError as e:
        app.logger.error("IntegrityError: {}".format(e))
        raise Forbidden("Unable to create log: IntegrityError")

    return new_tag_d
