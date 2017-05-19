from models import *
from collections import deque

# For debug purposes (app.logger)
from ucsnew.application import app

def get_items_list(query_itemnumber=None, query_membernumber=None, query_description=None, page=1, per_page=25):
   if query_itemnumber == None: query_itemnumber = ""
   if query_membernumber == None: query_membernumber = ""
   if query_description == None: query_description = ""
   if page == None: page = 1
   if per_page == None: per_page = 25

   app.logger.error("query_itemnumber: %s" % query_itemnumber)
   app.logger.error("query_membernumber: %s" % query_membernumber)
   app.logger.error("query_description: %s" % query_description)

   pagination = (Item.query
      .filter(Item.ID.like("%s%%" % query_itemnumber))
      .filter(Item.MemberNumber.like("%s%%" % query_membernumber))
      .filter(Item.Description.like("%%%s%%" % query_description))
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


def get_accounts_list(query_memberid=None, query_membernumber=None, query_lastname=None, query_phonenumber=None, page=1, per_page=25):
   if query_memberid == None: query_memberid = ""
   if query_membernumber == None: query_membernumber = ""
   if query_lastname == None: query_lastname = ""
   if query_phonenumber == None: query_phonenumber = ""
   if page == None: page = 1
   if per_page == None: per_page = 25

   app.logger.error("query_memberid: %s" % query_memberid)
   app.logger.error("query_membernumber: %s" % query_membernumber)
   app.logger.error("query_lastname: %s" % query_lastname)
   app.logger.error("query_phonenumber: %s" % query_phonenumber)

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
      .filter(Account.ID.like("%s%%" % query_memberid))
      .filter(Account.MemberNumber.like("%s%%" % query_membernumber))
      .filter(Account.LastName.like("%s%%" % query_lastname))
      .filter(Account.Phone.like("%s%%" % query_phonenumber))
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


