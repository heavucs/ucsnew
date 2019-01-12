import datetime
import re
import MySQLdb as sql
from decimal import Decimal, ROUND_HALF_UP

#from collections import deque

from .models import db
from .models import Member
from .models import Item
from .models import User

from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import BadRequest      # 400
from werkzeug.exceptions import Unauthorized    # 401
from werkzeug.exceptions import Forbidden       # 403
from werkzeug.exceptions import NotFound        # 404

from .application import app


### Business logic for Member DAOs

def get_members_list(q_memberid=None, q_membernumber=None, q_lastname=None,
        q_phonenumber=None, page=1, per_page=25):
    if q_phonenumber == None: q_phonenumber = ""

    page = page if page else 1
    per_page = per_page if per_page else 25

    db_member = (
                db.session.query(Member)
                .order_by(Member.membernumber.asc())
            )
    if q_membernumber:
        db_member = db_member.filter(Member.membernumber.like("%s%%"
                .format(q_membernumber)))
    if q_lastname:
        db_member = db_member.filter(Member.lastname.like("%s%%"
                .format(q_lastname)))
    if q_phonenumber:
        db_member = db_member.filter(Member.phonenumber.like("%s%%"
                .format(q_phonenumber)))

    if not app.config['LEGACY_UCS_ENABLED']:
        pagination = db_member.paginate(page=page, per_page=per_page,
            error_out=False)
        members_l = pagination.items
    else:
        members_l = db_member.all()

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

   new_mccount = Member(
      str(payload['membernumber']),
      datetime.date.today(), # Established
      str(payload['firstname']),
      str(payload['lastname']),
      str(payload['address']),
      str(payload['address2']),
      str(payload['city']),
      str(payload['state']),
      str(payload['zipcode']),
      str(payload['phone']),
      str(payload['email']),
      str(payload['password']),
      str(payload['question']),
      str(payload['answer']),
      str(''), # Activation Code
      datetime.datetime.date(),# Activated
      str('0'),# Admin
      str(''), # Browser
      str(''), # Notification
   )
   
   try:
      db.session.add(new_member)
      db.session.commit()

      new_account = (Member.query
         .filter(Member.membernumber == payload['membernumber'])
         .first()
      )
      # Created as an error since I'm not getting info messages
      app.logger.error("Created account %s: %s %s" %
              (new_member.membernumber, new_member.firstname, new_member.lastname)
              )

   except IntegrityError as e:
      app.logger.error("IntegrityError: %s" % str(e))
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
        db_item = db_item.filter(Item.members_membernumber.like("{}%%"
                .format(q_membernumber)))
    if q_description:
        db_item = db_item.filter(Item.description.like("%%{}%%"
                .format(q_description)))

    if not app.config['LEGACY_UCS_ENABLED']:
        pagination = db_item.paginate(page=page, per_page=per_page,
                error_out=False)
        items_l = pagination.items
    else:
        items_l = db_item.all()

        legacy_db = sql.connect(
                host=app.config['LEGACY_UCS_SQLHOST'],
                user=app.config['LEGACY_UCS_SQLUSER'],
                passwd=app.config['LEGACY_UCS_SQLPASS'],
                db=app.config['LEGACY_UCS_SQLDB']
                )
        legacy_db.c = legacy_db.cursor()
        nullstring = lambda x: x if x else ''
        legacy_db.c.execute("""SELECT ItemNumber, Description, Category, Subject,
                Publisher, Year, ISBN, `Condition`, ConditionDetail, NumItems,
                FridayPrice, SaturdayPrice, Donate, CheckedIn, CheckedOut, Status,
                Deleted, MemberNumber FROM Item {} {} {} limit {},{}"""
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
                'description': i[1],
                'category': i[2],
                'subject': i[3],
                'publisher': i[4],
                'year': i[5],
                'isbn': i[6],
                'condition': int(i[7]),
                'conditiondetail': i[8],
                'numitems': int(i[9]),
                'price': formatprice(str(i[10])),
                'discountprice': formatprice(str(i[11])),
                'donate': int(i[12]),
                'checkedin': formattime(str(i[13])),
                'checkedout': formattime(str(i[14])),
                'status': i[15],
                'deleted': int(i[16]),
                'membernumber': i[17],
                }
            items_l.append(item)

        #items_l = items_l[int(0 + (page - 1) * per_page):int(page * per_page)]

    return items_l

def create_item(payload):

   itemnumber = 1 + int(Item.query.
      filter(Item.MemberNumber == payload['MemberNumber']).
      count())

   new_item = Item(
      itemnumber,
      str(payload['MemberNumber']),
      str(payload['Description']),
      str(payload['Category']),
      str(payload['Subject']),
      str(payload['Publisher']),
      str(payload['Year']),
      str(payload['ISBN']),
      int(payload['Condition']),
      str(payload['ConditionDetail']),
      int(payload['NumItems']),
      Decimal(str(payload['FridayPrice'])).\
              quantize(Decimal(".01"), ROUND_HALF_UP),
      Decimal(str(payload['SaturdayPrice'])).\
              quantize(Decimal(".01"), ROUND_HALF_UP),
      bool(payload['Donate']),
      None,    # CheckedIn
      None,    # CheckedOut
      0,       # Status
      False,   # Deleted
      False,   # Printed
   )

   try:
      db.session.add(new_item)
      db.session.commit()

      new_item = (Item.query.
         filter(Item.MemberNumber == payload['MemberNumber']).
         filter(Item.ItemNumber == itemnumber).
         first()
      )
      # Created as an error since I'm not getting info messages
      app.logger.error("Created item %s: %s" % 
              (new_item.ID,new_item.Description))

   except IntegrityError as e:
      app.logger.error("IntegrityError: %s" % str(e))
      raise Forbidden("Unable to create resource: IntegrityError")

   return new_item


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


