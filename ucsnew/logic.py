import datetime
import re
import uuid
import barcode
from fpdf import FPDF
from io import BytesIO
import MySQLdb as sql
from decimal import Decimal, ROUND_HALF_UP

from flask import current_app

from .models import db
from .models import Member
from .models import Item
from .models import Transaction
from .models import Transaction_Item
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

def generate_mastersheet_pdf(membernumber):

    try:
        db_member = (
                    Member.query
                    .filter(Member.membernumber == membernumber)
                    .one()
                )
    except NoResultFound:
        raise NotFound
    member_d = db_member.as_api_dict()

    items_l = get_items(q_membernumber=membernumber)

    pdfstore = {}
    pdfstore['MEM'] = BytesIO()
    pdfstore['FILE'] = "{}/{}".format(
            app.config['TEMP_DIR'],
            membernumber + '.pdf',
            )

    class PDF_Mastersheet(FPDF):
        item_x = 1
        item_width = 0.75
        p_x = 1.75
        p_width = 0.25
        title_x = 2
        title_width = 2.5
        price_x = 4.5
        price_width = 0.75
        discount_x = 5.25
        discount_width = 0.75
        item2_x = 6
        item2_width = 0.75
        office_x = 6.75
        office_width = 0.75

        def __init__(self):
            super().__init__(orientation='P', unit='in', format='letter')

        def add_header_page(self):
            title_text = "{} {} {} MASTER SHEET".format(
                    app.config['ORG_NAME'],
                    datetime.datetime.today().year,
                    app.config['SALE_NAME'],
                    )
            mastersheet_msg1 = str(app.config['MASTERSHEET_MSG1'])
            mastersheet_msg2 = str(app.config['MASTERSHEET_MSG2'])

            self.add_page()
            self.set_fill_color(200, 200, 200)
            self.set_font_size(16)
            self.cell(7.5, 0.75, title_text, 0, 2, 'C')
            self.set_font('Arial', '', 8)
            self.set_xy(1, 1.15)
            self.cell(3.5, 0.3, mastersheet_msg1, 0, 2, 'C')
            self.set_xy(1, 1.25)
            self.cell(3.5, 0.3, mastersheet_msg2, 0, 2, 'C')

            self.set_font('Arial', 'B', 8)
            self.set_xy(self.item_x, 1.5)
            self.cell(self.item_width, 0.2, 'ITEM #', 1, 2, 'C')
            self.set_xy(self.p_x, 1.5)
            self.cell(self.p_width, 0.2, 'P', 1, 2, 'C')
            self.set_xy(self.title_x, 1.5)
            self.cell(self.title_width, 0.2, 'TITLE', 1, 2, 'C')
            self.set_xy(self.price_x, 1.5)
            self.cell(self.price_width, 0.2, 'PRICE', 1, 2, 'C')
            self.set_xy(self.discount_x, 1.5)
            self.cell(self.discount_width, 0.2, 'DISCOUNT', 1, 2, 'C')
            self.set_xy(self.item2_x, 1.5)
            self.cell(self.item2_width, 0.2, 'ITEM #', 1, 2, 'C')
            self.set_xy(self.office_x, 1.5)
            self.cell(self.office_width, 0.2, 'OFFICE USE', 1, 2, 'C')


        def add_footer_page(self, pagetotal, subtotal, islastpage=False):
            mastersheet_msg3 = str(app.config['MASTERSHEET_MSG3'])
            mastersheet_msg4 = str(app.config['MASTERSHEET_MSG4'])
            mastersheet_msg5 = str(app.config['MASTERSHEET_MSG5'])
            mastersheet_msg6 = str(app.config['MASTERSHEET_MSG6'])
            mastersheet_msg7 = str(app.config['MASTERSHEET_MSG7'])
            mastersheet_msg8 = str(app.config['MASTERSHEET_MSG8'])
            membernumber = str(member_d['membernumber'])
            firstname = str(member_d['firstname'])
            lastname = str(member_d['lastname'])
            phone = str("({}) {}-{}").format(
                    str(member_d['phone'])[0:3],
                    str(member_d['phone'])[3:6],
                    str(member_d['phone'])[6:10],
                    )
            address = str(member_d['address'])
            address2 = str(member_d['address2'])
            citystatezip = "{}, {} {}".format(
                    member_d['city'],
                    member_d['state'],
                    member_d['zipcode'],
                    )
            phone = str(member_d['phone'])
            email = str(member_d['email'])
            member_barcode = generate_barcode(membernumber, imgtype='PNG')
            pagetotal_str = "${}".format(
                    Decimal(pagetotal).quantize(Decimal('0.01'),
                        rounding=ROUND_HALF_UP)
                    )
            subtotal_other_str = "${}".format(
                    Decimal(subtotal).quantize(Decimal('0.01'),
                        rounding=ROUND_HALF_UP)
                    )
            subtotal_str = "${}".format(
                    Decimal(subtotal + pagetotal).quantize(Decimal('0.01'),
                        rounding=ROUND_HALF_UP)
                    )
            org_fee_rate = "LESS {} FEE {}%".format(
                    app.config['ORG_NAME'],
                    app.config['ORG_FEE_RATE'].quantize(
                        Decimal('0.01'), rounding=ROUND_HALF_UP),
                    )
            org_fee = (subtotal + pagetotal) * app.config['ORG_FEE_RATE']
            org_fee_str = "${}".format(org_fee.quantize(
                        Decimal('0.01'), rounding=ROUND_HALF_UP)
                    )
            grand_total = subtotal + pagetotal - org_fee
            grand_total_str = "${}".format(
                    Decimal(grand_total).quantize(Decimal('0.01'),
                        rounding=ROUND_HALF_UP)
                    )

            row_height = 0.185
            row_y = (25 * row_height) + 1.7
            self.set_fill_color(200, 200, 200)
            self.set_font('Arial', '', 8)
            self.set_xy(1, row_y)
            self.cell(3.5, row_height, mastersheet_msg3, 0, 2, 'L')

            self.set_font('Arial', 'B', 8)
            self.set_xy(self.price_x, row_y)
            self.cell(self.price_width * 3, row_height, 'SUBTOTAL', 0, 2, 'R')
            self.set_xy(self.office_x, row_y)
            self.cell(self.office_width, row_height, pagetotal_str, 1, 2, 'R', 1)
            row_y += row_height
            self.set_xy(self.price_x, row_y)
            self.cell(self.price_width * 3, row_height, 'SUBTOTAL FROM OTHER PAGES', 0, 2, 'R')
            self.set_xy(self.office_x, row_y)
            self.cell(self.office_width, row_height, subtotal_other_str, 1, 2, 'R', 1)
            row_y += row_height
            self.set_xy(self.price_x, row_y)
            self.cell(self.price_width * 3, row_height, 'SUBTOTAL', 0, 2, 'R')
            self.set_xy(self.office_x, row_y)
            self.cell(self.office_width, row_height, subtotal_str, 1, 2, 'R', 1)
            row_y += row_height
            self.set_xy(self.price_x, row_y)
            self.cell(self.price_width * 3, row_height, org_fee_rate, 0, 2, 'R')
            self.set_xy(self.office_x, row_y)
            if islastpage:
                self.cell(self.office_width, row_height, org_fee_str, 1, 2, 'R', 1)
            else:
                self.cell(self.office_width, row_height, '-----', 1, 2, 'C', 1)
            row_y += row_height
            self.set_xy(self.price_x, row_y)
            self.cell(self.price_width * 3, row_height, 'GRAND TOTAL', 0, 2, 'R')
            self.set_xy(self.office_x, row_y)
            if islastpage:
                self.cell(self.office_width, row_height, grand_total_str, 1, 2, 'R', 1)
            else:
                self.cell(self.office_width, row_height, '-----', 1, 2, 'C', 1)

            row_y += 2 * row_height
            self.rect(1, row_y, 3.75, 1.5)
            self.rect(1, row_y + 1.5, 3.75, 1.25)
            self.rect(4.75, row_y, 2.75, 2.75)
            row_y += 0.15
            self.set_font('Arial', 'B', 9)
            self.text(1.1, row_y, 'DROP-OFF AGREEMENT')
            self.text(1.1, row_y + 1.5, 'PICK-UP AGREEMENT')
            self.text(4.8, row_y, 'NAME')
            self.text(4.8, row_y + 0.4, 'ADDRESS')
            self.text(4.8, row_y + 0.8, 'CITY / STATE / ZIP')
            self.text(4.8, row_y + 1.1, 'PHONE')
            self.text(4.8, row_y + 1.4, 'EMAIL')
            self.set_font('Arial', '', 8)
            self.text(1.1, row_y + 0.11, mastersheet_msg4)
            self.text(1.1, row_y + 0.21, mastersheet_msg5)
            self.text(1.1, row_y + 0.31, mastersheet_msg6)
            self.rect(1.1, row_y + 0.41, 0.12, 0.12)
            self.rect(1.1, row_y + 0.56, 0.12, 0.12)
            self.rect(1.1, row_y + 0.71, 0.12, 0.12)
            self.text(1.3, row_y + 0.5, 'Donate All')
            self.text(1.3, row_y + 0.66, 'Pick-up By Seller')
            self.text(1.3, row_y + 0.81, 'Pick-up By Other')
            self.line(2.2, row_y + 0.81, 4.5, row_y + 0.81)
            self.text(1.1, row_y + 1.3, mastersheet_msg7)
            self.line(1.1, row_y + 1.17, 4.5, row_y + 1.17)
            self.rect(1.1, row_y + 1.65, 0.12, 0.12)
            self.rect(1.1, row_y + 1.80, 0.12, 0.12)
            self.rect(1.1, row_y + 1.95, 0.12, 0.12)
            self.text(1.3, row_y + 1.75, 'All Items')
            self.text(1.3, row_y + 1.91, 'Some Missing; Accepted')
            self.text(1.3, row_y + 2.07, 'Please search for #s')
            self.line(2.4, row_y + 2.07, 4.5, row_y + 2.07)
            self.text(1.1, row_y + 2.55, mastersheet_msg8)
            self.line(1.1, row_y + 2.42, 4.5, row_y + 2.42)

            self.set_font('Arial', '', 16)
            self.text(4.8, row_y + 0.18, lastname + ', ' + firstname)
            self.set_font('Arial', '', 8)
            self.text(4.8, row_y + 0.51, address)
            self.text(4.8, row_y + 0.61, address2)
            self.text(4.8, row_y + 0.91, citystatezip)
            self.text(4.8, row_y + 1.21, phone)
            self.text(4.8, row_y + 1.51, email)

            self.image(member_barcode, 5.25, row_y + 1.65, h=0.75, type='PNG')

        def add_item(self, i, item):
            item_d = item.as_api_dict()
            itemnumber = str(item_d['itemnumber'])
            description = str(item_d['description'])
            price = str(item_d['price'])
            discountprice = str(item_d['discountprice'])
            donate = item_d['donate']
            if donate == '0':
                donate_bool = False
            else:
                donate_bool = True
            status = item_d['status']
            transactions_l = get_transactions(q_itemnumber=item_d['uuid'])
            if len(transactions_l) > 0:
                for i in transactions_l:
                    if not i['ftime'].weekday() in app.config['DISCOUNT_PRICE_DAY']:
                        saleprice = item_d['price']
                        break
                    else:
                        continue
                else:   # If no break occurs # If item sold, but not at discount
                    saleprice = item_d['discountprice']
            else:
                saleprice = 0
            saleprice_str = "${}".format(Decimal(saleprice).quantize(
                    Decimal('0.01'), rounding=ROUND_HALF_UP))

            row_height = 0.185
            row_y = (i * row_height) + 1.7

            if not item_d['deleted'] == "1":
                if item_d['status'] == "0":
                    self.set_fill_color(0, 255, 255)
                elif item_d['status'] == "1":
                    self.set_fill_color(255, 255, 255)
                elif item_d['status'] == "2":
                    self.set_fill_color(0, 255, 0)
                elif item_d['status'] == "3":
                    self.set_fill_color(0, 0, 255)
                elif item_d['status'] == "4":
                    self.set_fill_color(255, 255, 0)
                else:
                    pass
            else:
                self.set_fill_color(255, 255, 255)

            self.set_font('Arial', 'B', 8)
            self.set_xy(self.item_x, row_y)
            self.cell(self.item_width, row_height, itemnumber, 1, 2, 'C', 1)
            self.set_font('Arial', '', 8)
            self.set_xy(self.p_x, row_y)
            if donate_bool:
                self.cell(self.p_width, row_height, 'X', 1, 2, 'C', 1)
            else:
                self.cell(self.p_width, row_height, '', 1, 2, 'C', 1)
            self.set_xy(self.title_x, row_y)
            self.cell(self.title_width, row_height, description, 1, 2, 'L', 1)
            self.set_xy(self.price_x, row_y)
            self.cell(self.price_width, row_height, price, 1, 2, 'R', 1)
            self.set_xy(self.discount_x, row_y)
            self.cell(self.discount_width, row_height, discountprice, 1, 2, 'R', 1)
            self.set_fill_color(200, 200, 200)
            self.set_font('Arial', 'B', 8)
            self.set_xy(self.item2_x, row_y)
            self.cell(self.item2_width, row_height, itemnumber, 1, 2, 'C', 1)
            self.set_xy(self.office_x, row_y)
            self.cell(self.office_width, row_height, saleprice_str, 1, 2, 'R', 1)

        def load_resource(self, reason, filename):
            if reason == "image":
                if is_instance(filename, "_io.BytesIO"):
                    f = io.ByesIO(filename)
                elif filename.startswith("http://") or filename.startswith("https://"):
                    f = BytesIO(urlopen(filename).read())
                elif filename.startswith("data"):
                    f = filename.split('base64,')[1]
                    f = base64.b64decode(f)
                    f = io.BytesIO(f)
                else:
                    f = open(filename, "rb")
                return f
            else:
                self.error("Unknown resource loading reason \"%s\"" % reason)

        # NOTE: Overriding parent _parsepng to allow loading BytesIO objects
        def _parsepng(self, name):
            from fpdf.py3k import PY3K
            #Extract info from a PNG file
            if isinstance(name, BytesIO):
                f = name
            elif name.startswith("http://") or name.startswith("https://"):
                   f = urlopen(name)
            else:
                f=open(name,'rb')
            if(not f):
                self.error("Can't open image file: "+str(name))
            #Check signature
            magic = f.read(8).decode("latin1")
            signature = '\x89'+'PNG'+'\r'+'\n'+'\x1a'+'\n'
            if not PY3K: signature = signature.decode("latin1")
            if(magic!=signature):
                self.error('Not a PNG file: '+str(name))
            #Read header chunk
            f.read(4)
            chunk = f.read(4).decode("latin1")
            if(chunk!='IHDR'):
                self.error('Incorrect PNG file: '+str(name))
            w=self._freadint(f)
            h=self._freadint(f)
            bpc=ord(f.read(1))
            if(bpc>8):
                self.error('16-bit depth not supported: '+str(name))
            ct=ord(f.read(1))
            if(ct==0 or ct==4):
                colspace='DeviceGray'
            elif(ct==2 or ct==6):
                colspace='DeviceRGB'
            elif(ct==3):
                colspace='Indexed'
            else:
                self.error('Unknown color type: '+str(name))
            if(ord(f.read(1))!=0):
                self.error('Unknown compression method: '+str(name))
            if(ord(f.read(1))!=0):
                self.error('Unknown filter method: '+str(name))
            if(ord(f.read(1))!=0):
                self.error('Interlacing not supported: '+str(name))
            f.read(4)
            dp='/Predictor 15 /Colors '
            if colspace == 'DeviceRGB':
                dp+='3'
            else:
                dp+='1'
            dp+=' /BitsPerComponent '+str(bpc)+' /Columns '+str(w)+''
            #Scan chunks looking for palette, transparency and image data
            pal=''
            trns=''
            data=bytes() if PY3K else str()
            n=1
            while n != None:
                n=self._freadint(f)
                type=f.read(4).decode("latin1")
                if(type=='PLTE'):
                    #Read palette
                    pal=f.read(n)
                    f.read(4)
                elif(type=='tRNS'):
                    #Read transparency info
                    t=f.read(n)
                    if(ct==0):
                        trns=[ord(substr(t,1,1)),]
                    elif(ct==2):
                        trns=[ord(substr(t,1,1)),ord(substr(t,3,1)),ord(substr(t,5,1))]
                    else:
                        pos=t.find('\x00'.encode("latin1"))
                        if(pos!=-1):
                            trns=[pos,]
                    f.read(4)
                elif(type=='IDAT'):
                    #Read image data block
                    data+=f.read(n)
                    f.read(4)
                elif(type=='IEND'):
                    break
                else:
                    f.read(n+4)
            if(colspace=='Indexed' and not pal):
                self.error('Missing palette in '+name)
            f.close()
            info = {'w':w,'h':h,'cs':colspace,'bpc':bpc,'f':'FlateDecode','dp':dp,'pal':pal,'trns':trns,}
            if(ct>=4):
                # Extract alpha channel
                data = zlib.decompress(data)
                color = b('')
                alpha = b('')
                if(ct==4):
                    # Gray image
                    length = 2*w
                    for i in range(h):
                        pos = (1+length)*i
                        color += b(data[pos])
                        alpha += b(data[pos])
                        line = substr(data, pos+1, length)
                        re_c = re.compile('(.).'.encode("ascii"), flags=re.DOTALL)
                        re_a = re.compile('.(.)'.encode("ascii"), flags=re.DOTALL)
                        color += re_c.sub(lambda m: m.group(1), line)
                        alpha += re_a.sub(lambda m: m.group(1), line)
                else:
                    # RGB image
                    length = 4*w
                    for i in range(h):
                        pos = (1+length)*i
                        color += b(data[pos])
                        alpha += b(data[pos])
                        line = substr(data, pos+1, length)
                        re_c = re.compile('(...).'.encode("ascii"), flags=re.DOTALL)
                        re_a = re.compile('...(.)'.encode("ascii"), flags=re.DOTALL)
                        color += re_c.sub(lambda m: m.group(1), line)
                        alpha += re_a.sub(lambda m: m.group(1), line)
                del data
                data = zlib.compress(color)
                info['smask'] = zlib.compress(alpha)
                if (self.pdf_version < '1.4'):
                    self.pdf_version = '1.4'
            info['data'] = data
            return info


    pdf = PDF_Mastersheet()
    pdf.orientation = 'P'
    pdf.unit = 'in'
    pdf.format = 'letter'
    pdf.set_auto_page_break(False)
    pdf.set_font('Arial')
    i = 0
    pagetotal = Decimal(0).quantize(Decimal('0.01'),
            rounding=ROUND_HALF_UP)
    subtotal = Decimal(0).quantize(Decimal('0.01'),
            rounding=ROUND_HALF_UP)
    if not i:
        pdf.add_header_page()
    items_l = get_items(q_membernumber=membernumber, per_page=100000)
    for item in items_l:
        pdf.add_item(i, item)
        transactions_l = get_transactions(q_itemnumber=item.uuid)
        if len(transactions_l) > 0:
            for i in transactions_l:
                if not i['ftime'].weekday() in app.config['DISCOUNT_PRICE_DAY']:
                    saleprice = item_d['price']
                    break
                else:
                    continue
            else:   # If no break occurs # If item sold, but not at discount
                saleprice = item_d['discountprice']
        else:
            saleprice = 0
        pagetotal += saleprice
        subtotal += saleprice
        if i < 25:
            i += 1
        else:
            i = 0
            pagetotal = 0
            pdf.add_header_page()
            pdf.add_footer_page(pagetotal, subtotal)
        #continue
    else:   # if no break occurs before end of list
        pdf.add_footer_page(pagetotal, subtotal, islastpage=True)


    pdf_file = pdfstore[app.config['TEMP_STORAGE']]
    if app.config['TEMP_STORAGE'] == 'MEM':
        pdf_file = BytesIO(pdf.output(dest='S').encode('latin-1'))
    if app.config['TEMP_STORAGE'] == 'FILE':
        pdf.output(name=pdf_file, dest='F')
        f = open("{}".format(pdfstore['FILE']), 'rb')
        pdf_file = BytesIO(f.read())

    pdf_file.seek(0)

    return pdf_file

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
        db_item = db_item.join(Transaction_Item)
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
        db_transaction = db_transaction.join(Transaction_Item)
        db_transaction = db_transaction.join(Item)
        db_transaction = db_transaction.filter(Item.uuid.like("%%{}%%"
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
        if len(get_items(q_transaction_uuid=old_transaction_uuid)) == 0:
            raise BadRequest("Unable to finalize Transaction {} with 0 items".format(
                old_transaction_uuid))
        db_transaction.ftime = datetime.datetime.now()

        create_auditlog(auth_user, {
                'text': "Transaction {} is being finalized".format(
                    db_transaction.uuid,
                    ),
                'tags': log_tags,
                }
            )

    if (db_transaction.finalized == True
            and finalized == False):

        create_auditlog(auth_user, {
                'text': "Transaction {} is being reopened".format(
                    db_transaction.uuid,
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
        if len(get_items(q_transaction_uuid=old_transaction_uuid)) == 0:
            raise BadRequest("Unable to finalize Transaction {} with 0 items".format(
                old_transaction_uuid))
        db_transaction.ftime = datetime.datetime.now()

        create_auditlog(auth_user, {
                'text': "Transaction {} is being finalized".format(
                    db_transaction.uuid,
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

    if (db_transaction.finalized == True
            and finalized == False):

        create_auditlog(auth_user, {
                'text': "Transaction {} is being reopened".format(
                    db_transaction.uuid,
                    ),
                'tags': log_tags,
                }
            )

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

    if datetime.datetime.now().weekday() in app.config['DISCOUNT_PRICE_DAY']:
        saleprice = db_item.discountprice
    else:
        saleprice = db_item.price

    log_tags[old_item_uuid] = 'item_uuid'

    if db_transaction.finalized:
        raise BadRequest("Transaction {} is finalized".format(
            old_transaction_uuid))

    try:
        db_transaction.items.append(db_item)
        db_transaction.total += saleprice
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

    if datetime.datetime.now().weekday() in app.config['DISCOUNT_PRICE_DAY']:
        saleprice = db_item.discountprice
    else:
        saleprice = db_item.price

    log_tags[old_item_uuid] = 'item_uuid'

    if db_transaction.finalized:
        raise BadRequest("Transaction {} is finalized".format(
            old_transaction_uuid))

    try:
        db_transaction.items.remove(db_item)
        db_transaction.total -= saleprice
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

def generate_receipt_pdf(transaction_uuid):

    try:
        db_transaction = (
                    Transaction.query
                    .filter(Transaction.uuid == transaction_uuid)
                    .one()
                )
    except NoResultFound:
        raise NotFound
    transaction_d = db_transaction.as_api_dict()

    if not transaction_d['finalized']:
        raise BadRequest("Transaction {} must be finalized".format(
            transaction_uuid))

    items_l = get_items(q_transaction_uuid=transaction_d['uuid'])

    pdfstore = {}
    pdfstore['MEM'] = BytesIO()
    pdfstore['FILE'] = "{}/{}".format(
            app.config['TEMP_DIR'],
            transaction_uuid + '.pdf',
            )

    class PDF_Transaction(FPDF):

        def header(self):
            uuid = str(transaction_d['uuid'])
            ftime = str(transaction_d['ftime'].strftime("%m/%d/%Y %H:%M:%S"))
            user = str(transaction_d['user_username'])
            transaction_barcode = generate_barcode(uuid, imgtype='PNG')

            self.set_font('Arial', 'B', 10)
            self.cell(78, 5, 'Transaction UUID', 'TL', 0, 'L')
            self.image(transaction_barcode, 60, 198, h=28, type='PNG')
            self.cell(93, 5, 'Date', 'T', 0, 'L')
            self.cell(23, 5, 'User', 'TR', 1, 'L')
            self.set_font('Arial', '', 10)
            self.cell(78, 5, uuid, 'BL', 0, 'L')
            self.cell(93, 5, ftime, 'B', 0, 'L')
            self.cell(23, 5, user, 'BR', 1, 'L')
            self.ln(5)
            self.set_font('Arial', 'B', 10)
            self.cell(158, 5, 'Description', 0, 0, 'L')
            self.cell(21, 5, 'Item Count', 0, 0, 'L')
            self.cell(15, 5, 'Price', 0, 1, 'R')

        def footer(self):
            total_items = str(len(items_l))
            subtotal_sales = transaction_d['total'].quantize(
                    Decimal('0.01'), rounding=ROUND_HALF_UP)
            sales_tax_rate = str((app.config['SALES_TAX_RATE'] * 100).quantize(
                    Decimal('0.01'), rounding=ROUND_HALF_UP))
            sales_tax = (subtotal_sales * app.config['SALES_TAX_RATE']).quantize(
                    Decimal('0.01'), rounding=ROUND_HALF_UP)
            grand_total = (subtotal_sales + sales_tax).quantize(
                    Decimal('0.01'), rounding=ROUND_HALF_UP)
            PAYMENT_TYPES = ['CASH', 'CHECK', 'CREDIT', 'OTHER']
            payment_method = PAYMENT_TYPES[int(transaction_d['payment_method'])]
            receipt_checkspayable = app.config['RECEIPT_CHECKSPAYABLE']
            receipt_logo = str(app.config['RECEIPT_LOGO'])
            receipt_msg1 = str(app.config['RECEIPT_MSG1'])
            receipt_msg2 = str(app.config['RECEIPT_MSG2'])
            receipt_msg3 = str(app.config['RECEIPT_MSG3'])
            receipt_msg4 = str(app.config['RECEIPT_MSG4'])
            receipt_msg5 = str(app.config['RECEIPT_MSG5'])
            receipt_msg6 = str(app.config['RECEIPT_MSG6'])
            receipt_msg7 = str(app.config['RECEIPT_MSG7'])
            receipt_msg8 = str(app.config['RECEIPT_MSG8'])

            self.set_y(-100)
            self.set_font('Arial', '', 12)
            self.cell(165, 5, 'Total Items', 'T', 0, 'L')
            self.cell(30, 5, total_items, 'T', 1, 'R')
            self.cell(165, 5, 'Subtotal Sales', 0, 0, 'L')
            self.cell(30, 5, "${}".format(subtotal_sales), 0, 1, 'R')
            self.cell(165, 5, 'Sales Tax ({}%)'.format(sales_tax_rate), 0, 0, 'L')
            self.cell(30, 5, "${}".format(sales_tax), 0, 1, 'R')
            self.cell(165, 5, 'Grand Total', 0, 0, 'L')
            self.cell(30, 5, "${}".format(grand_total), 0, 1, 'R')
            self.cell(165, 5, 'Payment Type', 0, 0, 'L')
            self.cell(30, 5, payment_method, 0, 1, 'R')
            self.ln(3)
            self.cell(195, 5, receipt_checkspayable, 0, 1, 'C')
            try:
                self.image(receipt_logo, 90, self.get_y(), 30)
            except:
                app.logger.warning("Unable to load image: {}"
                        .format(receipt_logo))
            self.ln(11)
            self.cell(195, 5, receipt_msg1, 0, 1, 'L')
            self.cell(195, 5, receipt_msg2, 0, 1, 'L')
            self.cell(195, 5, receipt_msg3, 0, 1, 'l')
            self.cell(195, 5, receipt_msg4, 0, 1, 'L')
            self.cell(195, 5, receipt_msg5, 0, 1, 'L')
            self.cell(195, 5, receipt_msg6, 0, 1, 'L')
            self.cell(195, 5, receipt_msg7, 0, 1, 'C')
            self.cell(195, 5, receipt_msg8, 0, 1, 'C')
            # Position at 1 cm from bottom
            self.set_y(-10)
            # Arial italic 8
            self.set_font('Arial', 'I', 8)
            # Page number
            self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')

        def add_item(self, description, numitems, sellprice):
            self.set_font('Arial', '', 10)
            self.cell(158, 5, str(description), 0, 0, 'L')
            self.cell(21, 5, str(numitems), 0, 0, 'L')
            self.cell(15, 5, str(sellprice), 0, 1, 'R')

        def load_resource(self, reason, filename):
            if reason == "image":
                if is_instance(filename, "_io.BytesIO"):
                    f = io.ByesIO(filename)
                elif filename.startswith("http://") or filename.startswith("https://"):
                    f = BytesIO(urlopen(filename).read())
                elif filename.startswith("data"):
                    f = filename.split('base64,')[1]
                    f = base64.b64decode(f)
                    f = io.BytesIO(f)
                else:
                    f = open(filename, "rb")
                return f
            else:
                self.error("Unknown resource loading reason \"%s\"" % reason)

        # NOTE: Overriding parent _parsepng to allow loading BytesIO objects
        def _parsepng(self, name):
            from fpdf.py3k import PY3K
            #Extract info from a PNG file
            if isinstance(name, BytesIO):
                f = name
            elif name.startswith("http://") or name.startswith("https://"):
                   f = urlopen(name)
            else:
                f=open(name,'rb')
            if(not f):
                self.error("Can't open image file: "+str(name))
            #Check signature
            magic = f.read(8).decode("latin1")
            signature = '\x89'+'PNG'+'\r'+'\n'+'\x1a'+'\n'
            if not PY3K: signature = signature.decode("latin1")
            if(magic!=signature):
                self.error('Not a PNG file: '+str(name))
            #Read header chunk
            f.read(4)
            chunk = f.read(4).decode("latin1")
            if(chunk!='IHDR'):
                self.error('Incorrect PNG file: '+str(name))
            w=self._freadint(f)
            h=self._freadint(f)
            bpc=ord(f.read(1))
            if(bpc>8):
                self.error('16-bit depth not supported: '+str(name))
            ct=ord(f.read(1))
            if(ct==0 or ct==4):
                colspace='DeviceGray'
            elif(ct==2 or ct==6):
                colspace='DeviceRGB'
            elif(ct==3):
                colspace='Indexed'
            else:
                self.error('Unknown color type: '+str(name))
            if(ord(f.read(1))!=0):
                self.error('Unknown compression method: '+str(name))
            if(ord(f.read(1))!=0):
                self.error('Unknown filter method: '+str(name))
            if(ord(f.read(1))!=0):
                self.error('Interlacing not supported: '+str(name))
            f.read(4)
            dp='/Predictor 15 /Colors '
            if colspace == 'DeviceRGB':
                dp+='3'
            else:
                dp+='1'
            dp+=' /BitsPerComponent '+str(bpc)+' /Columns '+str(w)+''
            #Scan chunks looking for palette, transparency and image data
            pal=''
            trns=''
            data=bytes() if PY3K else str()
            n=1
            while n != None:
                n=self._freadint(f)
                type=f.read(4).decode("latin1")
                if(type=='PLTE'):
                    #Read palette
                    pal=f.read(n)
                    f.read(4)
                elif(type=='tRNS'):
                    #Read transparency info
                    t=f.read(n)
                    if(ct==0):
                        trns=[ord(substr(t,1,1)),]
                    elif(ct==2):
                        trns=[ord(substr(t,1,1)),ord(substr(t,3,1)),ord(substr(t,5,1))]
                    else:
                        pos=t.find('\x00'.encode("latin1"))
                        if(pos!=-1):
                            trns=[pos,]
                    f.read(4)
                elif(type=='IDAT'):
                    #Read image data block
                    data+=f.read(n)
                    f.read(4)
                elif(type=='IEND'):
                    break
                else:
                    f.read(n+4)
            if(colspace=='Indexed' and not pal):
                self.error('Missing palette in '+name)
            f.close()
            info = {'w':w,'h':h,'cs':colspace,'bpc':bpc,'f':'FlateDecode','dp':dp,'pal':pal,'trns':trns,}
            if(ct>=4):
                # Extract alpha channel
                data = zlib.decompress(data)
                color = b('')
                alpha = b('')
                if(ct==4):
                    # Gray image
                    length = 2*w
                    for i in range(h):
                        pos = (1+length)*i
                        color += b(data[pos])
                        alpha += b(data[pos])
                        line = substr(data, pos+1, length)
                        re_c = re.compile('(.).'.encode("ascii"), flags=re.DOTALL)
                        re_a = re.compile('.(.)'.encode("ascii"), flags=re.DOTALL)
                        color += re_c.sub(lambda m: m.group(1), line)
                        alpha += re_a.sub(lambda m: m.group(1), line)
                else:
                    # RGB image
                    length = 4*w
                    for i in range(h):
                        pos = (1+length)*i
                        color += b(data[pos])
                        alpha += b(data[pos])
                        line = substr(data, pos+1, length)
                        re_c = re.compile('(...).'.encode("ascii"), flags=re.DOTALL)
                        re_a = re.compile('...(.)'.encode("ascii"), flags=re.DOTALL)
                        color += re_c.sub(lambda m: m.group(1), line)
                        alpha += re_a.sub(lambda m: m.group(1), line)
                del data
                data = zlib.compress(color)
                info['smask'] = zlib.compress(alpha)
                if (self.pdf_version < '1.4'):
                    self.pdf_version = '1.4'
            info['data'] = data
            return info


    pdf = PDF_Transaction()
    pdf.set_margins(10, 10)
    pdf.set_auto_page_break(False)
    pdf.set_font('Arial')
    pdf.alias_nb_pages()

    i_num = 0
    for i in items_l:
        if i_num % 30 == 0:
            pdf.add_page()
        i_num += 1

        item = i.as_api_dict()
        if transaction_d['ftime'].weekday() in app.config['DISCOUNT_PRICE_DAY']:
            price = item['discountedprice'].quantize(
                    Decimal('0.01'), rounding=ROUND_HALF_UP)
        else:
            price = item['price'].quantize(
                    Decimal('0.01'), rounding=ROUND_HALF_UP)
        pdf.add_item(item['description'], item['numitems'], price)

    pdf_file = pdfstore[app.config['TEMP_STORAGE']]
    if app.config['TEMP_STORAGE'] == 'MEM':
        pdf_file = BytesIO(pdf.output(dest='S').encode('latin-1'))
    if app.config['TEMP_STORAGE'] == 'FILE':
        pdf.output(name=pdf_file, dest='F')
        f = open("{}".format(pdfstore['FILE']), 'rb')
        pdf_file = BytesIO(f.read())

    pdf_file.seek(0)

    return pdf_file


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

def generate_barcode(codedata, imgtype='SVG'):

    if app.config['BARCODE_SYMBOLOGY'] in barcode.PROVIDED_BARCODES:

        app.logger.info("Generating barcode for {}".format(codedata))

        imgstore = {}
        imgstore['MEM'] = BytesIO()
        imgstore['FILE'] = "{}/{}".format(
                app.config['TEMP_DIR'],
                codedata
                )

        barcode_img = imgstore[app.config['TEMP_STORAGE']]
        if imgtype == 'SVG':
            barcode.generate(
                app.config['BARCODE_SYMBOLOGY'],
                codedata,
                output=barcode_img
                )
        elif imgtype == 'PNG':
            barcode.generate(
                app.config['BARCODE_SYMBOLOGY'],
                codedata,
                writer=barcode.writer.ImageWriter(),
                output=barcode_img
                )
    else:
        app.logger.error("Unknown Barcode Symbology: {}".format(
            app.config['BARCODE_SYMBOLOGY'])
            )
        app.logger.error("Set config BARCODE_SYMBOLOGY to one of the following:")
        app.logger.error("{}".format(PROVIDES_BARCODES))

    if app.config['TEMP_STORAGE'] == 'FILE':
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

        tags = {}
        for tag in get_auditlogtags(new_log['uuid']):
            tags[tag.as_api_dict()['tag']] = tag.as_api_dict()['tagtype']
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
