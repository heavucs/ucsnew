from sqlalchemy.exc import IntegrityError
from models import *
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
   app.logger.error("Items: %s" % pagination.items)
   app.logger.error("next_num: %s" % pagination.next_num)
   app.logger.error("page: %s" % pagination.page)
   app.logger.error("per_page: %s" % pagination.per_page)
   app.logger.error("total: %s" % pagination.total)
   app.logger.error("query: %s" % pagination.query)

   app.logger.error("Respons JSON: %s" % pagination.items)
   app.logger.error("Respons JSON: %s" % type(pagination.items[0]))

   return pagination.items

#def create_item(q_membernumber,q_description,q_category,q_subject,q_publisher,q_year,q_isbn,q_condition,q_conditiondetail,q_numitems,q_fridayprice,q_saturdayprice,q_donate):
def create_item(payload):
   itemnumber = int(Item.query.filter(Item.MemberNumber == payload['MemberNumber']).count()) + 1
   membernumber = str(payload['MemberNumber'])
   description = str(payload['Description'])
   category = str(payload['Category'])
   subject = str(payload['Subject'])
   publisher = str(payload['Publisher'])
   year = str(payload['Year'])
   isbn = str(payload['ISBN'])
   condition = int(payload['Condition'])
   conditiondetail = str(payload['ConditionDetail'])
   numitems = int(payload['NumItems'])
   fridayprice = Decimal(str(payload['FridayPrice'])).quantize(Decimal(".01"), ROUND_HALF_UP)
   saturdayprice = Decimal(str(payload['SaturdayPrice'])).quantize(Decimal(".01"), ROUND_HALF_UP)
   #fridayprice = float(q_fridayprice)
   #saturdayprice = float(q_saturdayprice)
   donate = bool(payload['Donate'])
   checkedin = None
   checkedout = None
   status = 0
   deleted = False
   printed = False
   
   new_item = Item(itemnumber,membernumber,description,category,subject,publisher,year,isbn,condition,conditiondetail,numitems,fridayprice,saturdayprice,donate,checkedin,checkedout,status,deleted,printed)

   try:
      db.session.add(new_item)
      db.session.commit()

      new_item = (Item.query
         .filter(Item.MemberNumber == payload['MemberNumber'])
         .filter(Item.ItemNumber == itemnumber)
         .first()
      )
      app.logger.info("Created item %s: %s" % (new_item.ID,new_item.Description))
      # Created as an error since I'm not getting info messages
      app.logger.error("Created item %s: %s" % (new_item.ID,new_item.Description))

   except IntegrityError as e:
      app.logger.warning("IntegrityError: %s" % str(e))
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
      .with_entities(
         Account.ID.label('ID').label('ID'),
         Account.MemberNumber.label('MemberNumber'),
         Account.FirstName.label('FirstName'),
         Account.LastName.label('LastName'),
         db.func.count(Item.ID).label('Items'),
         Account.Activated.label('Activated'),
         Account.Phone.label('Phone'),
         )
      .filter(Account.ID.like("%s%%" % q_memberid))
      .filter(Account.MemberNumber.like("%s%%" % q_membernumber))
      .filter(Account.LastName.like("%s%%" % q_lastname))
      .filter(Account.Phone.like("%s%%" % q_phonenumber))
      .group_by(Account.MemberNumber)
      .paginate(page=page, per_page=per_page, error_out=False)
      )

   app.logger.error("Accounts: %s" % pagination.items)
   app.logger.error("next_num: %s" % pagination.next_num)
   app.logger.error("page: %s" % pagination.page)
   app.logger.error("per_page: %s" % pagination.per_page)
   app.logger.error("total: %s" % pagination.total)
   app.logger.error("query: %s" % pagination.query)

   # Using .with_entities in the sqlalchemy causes its output to be a list instead of an object
   # This class is used to reconstruct an object
   # Maybe there is a better way of doing this
   class cols(object):
      def __init__(self,ID,MemberNumber,FirstName,LastName,Items,Activated,Phone):
         self.ID = int(ID)
         self.MemberNumber = MemberNumber
         self.FirstName = FirstName
         self.LastName = LastName
         self.Items = int(Items)
         self.Activated = Activated
         self.Phone = Phone
   results = []
   for i in pagination.items:
      results.append(cols(i.ID,i.MemberNumber,i.FirstName,i.LastName,i.Items,i.Activated,i.Phone))

   return results


