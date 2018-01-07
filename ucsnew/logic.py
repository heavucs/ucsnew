from sqlalchemy.exc import IntegrityError
import datetime
from .models import db, Member, Item, User
from decimal import Decimal
#from collections import deque

from werkzeug.exceptions import BadRequest      # 400
from werkzeug.exceptions import Unauthorized    # 401
from werkzeug.exceptions import Forbidden       # 403
from werkzeug.exceptions import NotFound        # 404

from ucsnew.application import app


### Business logic for Member DAOs

def get_members_list(q_memberid=None, q_membernumber=None, q_lastname=None, q_phonenumber=None, page=1, per_page=25):
   if q_memberid == None: q_memberid = ""
   if q_membernumber == None: q_membernumber = ""
   if q_lastname == None: q_lastname = ""
   if q_phonenumber == None: q_phonenumber = ""
   if page == None: page = 1
   if per_page == None: per_page = 25

   app.logger.error("query_memberid: %s" % q_memberid)
   app.logger.error("query_membernumber: %s" % q_membernumber)
   app.logger.error("query_lastname: %s" % q_lastname)
   app.logger.error("query_phonenumber: %s" % q_phonenumber)

   pagination = (Member.query
      .join(Item, Member.membernumber == Item.membernumber)
      #.with_entities(
      #   Account.ID.label('ID').label('ID'),
      #   Account.MemberNumber.label('MemberNumber'),
      #   Account.FirstName.label('FirstName'),
      #   Account.LastName.label('LastName'),
      #   db.func.count(Item.ID).label('Items'),
      #   Account.Activated.label('Activated'),
      #   Account.Phone.label('Phone'),
      #)
      .filter(Member.id.like("%s%%" % q_memberid))
      .filter(Member.membernumber.like("%s%%" % q_membernumber))
      .filter(Member.lastname.like("%s%%" % q_lastname))
      .filter(Member.phone.like("%s%%" % q_phonenumber))
      .group_by(Member.membernumber)
      .paginate(page=page, per_page=per_page, error_out=False)
   )

   app.logger.error("items: %s" % pagination.items)
   app.logger.error("next_num: %s" % pagination.next_num)
   app.logger.error("page: %s" % pagination.page)
   app.logger.error("per_page: %s" % pagination.per_page)
   app.logger.error("total: %s" % pagination.total)
   app.logger.error("query: %s" % pagination.query)

   # Using .with_entities in the sqlalchemy causes its output to be a list instead of an object
   # This class is used to reconstruct an object
   # Maybe there is a better way of doing this
   #class cols(object):
   #   def __init__(self,ID,MemberNumber,FirstName,LastName,Items,Activated,Phone):
   #      self.ID = int(ID)
   #      self.MemberNumber = MemberNumber
   #      self.FirstName = FirstName
   #      self.LastName = LastName
   #      self.Items = int(Items)
   #      self.Activated = Activated
   #      self.Phone = Phone
   #results = []
   #for i in pagination.items:
   #   results.append(cols(i.ID,i.MemberNumber,i.FirstName,i.LastName,i.Items,i.Activated,i.Phone))

   #return results
   return pagination.items

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
      app.logger.error("Created account %s: %s %s" % (new_member.membernumber, new_member.firstname, new_member.lastname))

   except IntegrityError as e:
      app.logger.error("IntegrityError: %s" % str(e))
      raise Forbidden("Unable to create resource: IntegrityError")

   return new_member


### Business logic for Item DAOs

def get_items_list(q_itemnumber=None, q_membernumber=None, q_description=None, page=1, per_page=25):
   #if q_itemnumber == None: q_itemnumber = ""
   #if q_membernumber == None: q_membernumber = ""
   #if q_description == None: q_description = ""
   #if page == None: page = 1
   #if per_page == None: per_page = 25

   #app.logger.error("q_itemnumber: %s" % q_itemnumber)
   #app.logger.error("q_membernumber: %s" % q_membernumber)
   #app.logger.error("q_description: %s" % q_description)

   #pagination = (Item.query
   #   .filter(Item.id.like("%s%%" % q_itemnumber))
   #   .filter(Item.membernumber.like("%s%%" % q_membernumber))
   #   .filter(Item.description.like("%%%s%%" % q_description))
   #   .paginate(page=page, per_page=per_page, error_out=False)
   #)

   #app.logger.error("items: %s" % pagination.items)
   #app.logger.error("next_num: %s" % pagination.next_num)
   #app.logger.error("page: %s" % pagination.page)
   #app.logger.error("per_page: %s" % pagination.per_page)
   #app.logger.error("total: %s" % pagination.total)
   #app.logger.error("query: %s" % pagination.query)

   #app.logger.error("Response: %s" % pagination.items)
   #app.logger.error("Response: %s" % type(pagination.items[0]))

   #return pagination.items

   #items_l = deque(map(lambda x: x.as_api_dict(), Item.query.all()))
   items_l = Item.query.all()

   app.logger.info("Items list retrieved")

   return items_l

def create_item(payload):

   itemnumber = 1 + int(Item.query
      .filter(Item.MemberNumber == payload['MemberNumber'])
      .count())

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
      Decimal(str(payload['FridayPrice'])).quantize(Decimal(".01"), ROUND_HALF_UP),
      Decimal(str(payload['SaturdayPrice'])).quantize(Decimal(".01"), ROUND_HALF_UP),
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

      new_item = (Item.query
         .filter(Item.MemberNumber == payload['MemberNumber'])
         .filter(Item.ItemNumber == itemnumber)
         .first()
      )
      # Created as an error since I'm not getting info messages
      app.logger.error("Created item %s: %s" % (new_item.ID,new_item.Description))

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
            'password': generate_password_hash(str(payload['password']), app.config['PW_HASH']),
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

        db_user = (User.query
            .filter(User.username == new_user['username'])
            .first()
        )

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
        payload['password'] = generate_password_hash(str(payload['password']), app.config['PW_HASH'])

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

    return {'message': "User %s successfully deleted by %s" % (old_username, auth_user)}


