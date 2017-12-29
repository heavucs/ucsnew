from sqlalchemy.exc import IntegrityError
import datetime
from .models import Item, Account, Checker
from decimal import *

# For debug purposes (app.logger)
from ucsnew.application import app

def get_items_list(q_itemnumber=None, q_membernumber=None, q_description=None, page=1, per_page=25):
   if q_itemnumber == None: q_itemnumber = ""
   if q_membernumber == None: q_membernumber = ""
   if q_description == None: q_description = ""
   if page == None: page = 1
   if per_page == None: per_page = 25

   app.logger.error("q_itemnumber: %s" % q_itemnumber)
   app.logger.error("q_membernumber: %s" % q_membernumber)
   app.logger.error("q_description: %s" % q_description)

   pagination = (Item.query
      .filter(Item.ID.like("%s%%" % q_itemnumber))
      .filter(Item.MemberNumber.like("%s%%" % q_membernumber))
      .filter(Item.Description.like("%%%s%%" % q_description))
      .paginate(page=page, per_page=per_page, error_out=False)
   )

   app.logger.error("items: %s" % pagination.items)
   app.logger.error("next_num: %s" % pagination.next_num)
   app.logger.error("page: %s" % pagination.page)
   app.logger.error("per_page: %s" % pagination.per_page)
   app.logger.error("total: %s" % pagination.total)
   app.logger.error("query: %s" % pagination.query)

   app.logger.error("Response: %s" % pagination.items)
   app.logger.error("Response: %s" % type(pagination.items[0]))

   return pagination.items

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


def get_accounts_list(q_memberid=None, q_membernumber=None, q_lastname=None, q_phonenumber=None, page=1, per_page=25):
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

   pagination = (Account.query
      .join(Item, Account.MemberNumber == Item.MemberNumber)
      #.with_entities(
      #   Account.ID.label('ID').label('ID'),
      #   Account.MemberNumber.label('MemberNumber'),
      #   Account.FirstName.label('FirstName'),
      #   Account.LastName.label('LastName'),
      #   db.func.count(Item.ID).label('Items'),
      #   Account.Activated.label('Activated'),
      #   Account.Phone.label('Phone'),
      #)
      .filter(Account.ID.like("%s%%" % q_memberid))
      .filter(Account.MemberNumber.like("%s%%" % q_membernumber))
      .filter(Account.LastName.like("%s%%" % q_lastname))
      .filter(Account.Phone.like("%s%%" % q_phonenumber))
      .group_by(Account.MemberNumber)
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

def create_account(payload):

   new_account = Account(
      str(payload['MemberNumber']),
      datetime.date.today(),   # Established
      str(payload['FirstName']),
      str(payload['LastName']),
      str(payload['Address']),
      str(payload['Address2']),
      str(payload['City']),
      str(payload['State']),
      str(payload['Zip']),
      str(payload['Phone']),
      str(payload['Email']),
      str(payload['Password']),
      str(payload['Question']),
      str(payload['Answer']),
      str(''), # Activation Code
      datetime.date.today(),# Activated
      False,   # Admin
      str(''), # Browser
      str(''), # Notification
   )
   
   try:
      db.session.add(new_account)
      db.session.commit()

      new_account = (Account.query
         .filter(Account.MemberNumber == payload['MemberNumber'])
         .first()
      )
      # Created as an error since I'm not getting info messages
      app.logger.error("Created account %s: %s %s" % (new_account.MemberNumber,new_account.FirstName,new_account.LastName))

   except IntegrityError as e:
      app.logger.error("IntegrityError: %s" % str(e))
      raise Forbidden("Unable to create resource: IntegrityError")

   return new_account


def get_checkers_list(q_loginid=None, q_barcode=None, page=1, per_page=25):
   if q_loginid == None: q_loginid = ""
   if q_barcode == None: q_barcode = ""
   if page == None: page = 1
   if per_page == None: per_page = 25

   app.logger.error("q_loginid: %s" % q_loginid)
   app.logger.error("q_barcode: %s" % q_barcode)

   pagination = (Checker.query
      .filter(Checker.LoginID.like("%s%%" % q_loginid))
      .filter(Checker.Barcode.like("%s%%" % q_barcode))
      .paginate(page=page, per_page=per_page, error_out=False)
   )

   app.logger.error("items: %s" % pagination.items)
   app.logger.error("next_num: %s" % pagination.next_num)
   app.logger.error("page: %s" % pagination.page)
   app.logger.error("per_page: %s" % pagination.per_page)
   app.logger.error("total: %s" % pagination.total)
   app.logger.error("query: %s" % pagination.query)

   app.logger.error("Response: %s" % pagination.items)
   app.logger.error("Response: %s" % type(pagination.items[0]))

   return pagination.items

def create_checker(payload):

   new_checker = Checker(
      str(payload['LoginID']),
      str(payload['FirstName']),
      str(payload['LastName']),
      str(payload['Barcode']),
      str(payload['Admin']),
   )
   
   try:
      db.session.add(new_checker)
      db.session.commit()

      new_checker = (Checker.query
         .filter(Checker.LoginID == payload['LoginID'])
         .first()
      )
      # Created as an error since I'm not getting info messages
      app.logger.error("Created account %s: %s %s" % (new_account.MemberNumber,new_account.FirstName,new_account.LastName))

   except IntegrityError as e:
      app.logger.error("IntegrityError: %s" % str(e))
      raise Forbidden("Unable to create resource: IntegrityError")

   return new_account


