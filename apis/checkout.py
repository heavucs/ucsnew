from flask_restplus import Namespace, Resource, fields
from ucsnew.core.logic import *

# For debug purposes (app.logger)
from ucsnew.application import app

api = Namespace('Checkout', Description='Checkout related functions')

item = api.model('Item', {
   'ID': fields.String(readOnly=True, description='AutoIncremented ID'),
   'MemberNumber': fields.String(required=True, description='Vendor\'s Account Number'),
   'ItemNumber': fields.String(required=True, description='ItemNumber used for barcodes'),
   'Description': fields.String(required=True, description='Description of the item'),
   'Category': fields.String(Required=True, description='Item\'s Category'),
   'NumItems': fields.Integer(Required=True, description='Number of items included in "Item" e.g. a set of books'),
   'Status': fields.Integer(Required=True, description='Represents Item status, 0 not checked-in, 1 checked-in, 2 sold'),
   'FridayPrice': fields.String(Required=True, description='Friday price'),
   'SaturdayPrice': fields.String(Required=True, description='Saturday price'),
})

@api.route('/items', methods=['GET'])
@api.doc(params={
   'query_itemnumber': 'Query Item Number',
   'query_membernumber': 'Query Member Number',
   'query_description': 'Query Description',
   'page': 'Page number',
   'per_page': 'Results per page',
   })
class ItemList(Resource):
   @api.doc('list_items')
   @api.marshal_list_with(item)
   @api.response(200, 'OK', model=item)
   def get(self, query_itemnumber=None, query_membernumber=None, query_description=None, page=1, per_page=25):
      '''List items'''

      parser = api.parser()

      parser.add_argument('query_itemnumber', type=str, location='args')
      parser.add_argument('query_membernumber', type=str, location='args')
      parser.add_argument('query_description', type=str, location='args')
      parser.add_argument('page', type=int, location='args')
      parser.add_argument('per_page', type=int, location='args')
      
      args = parser.parse_args()

      results = get_items_list(
         args['query_itemnumber'],
         args['query_membernumber'],
         args['query_description'],
         args['page'],
         args['per_page'],
      )

      return results, 200

#@api.route('/')
#def index():
#   return render_template('index.html')
#
#@api.route('/checkout/account', methods=['GET','POST'])
#def account(pageid="account"):
#   if request.method == 'POST':
#      if request.form['ID']:
#         ID = request.form['ID']
#      else:
#         ID = ""
#      if request.form['MemberNumber']:
#         MemberNumber = request.form['MemberNumber']
#      else:
#         MemberNumber = ""
#      if request.form['LastName']:
#         LastName = request.form['LastName']
#      else:
#         LastName = ""
#      if request.form['PhoneNumber']:
#         PhoneNumber = request.form['PhoneNumber']
#      else:
#         PhoneNumber = ""
#      if request.form['Page']:
#         if not request.form['Page'] == 'NaN':
#            page = int(request.form['Page'])
#         else:
#            page = 1
#      else:
#         page = 1
#      pagination = (Account.query
#         .join(Item, Account.MemberNumber == Item.MemberNumber)
#         .with_entities(Account.ID,Account.MemberNumber,Account.FirstName,Account.LastName,db.func.count(Item.ID).label("Items"),Account.Activated)
#         .filter(Account.ID.like("%s%s"%(ID,"%")))
#         .filter(Account.MemberNumber.like("%s%s"%(MemberNumber,"%")))
#         .filter(Account.LastName.like("%s%s"%(LastName,"%")))
#         .filter(Account.Phone.like("%s%s"%(PhoneNumber,"%")))
#         .group_by(Account.MemberNumber)
#         .paginate(page=page, per_page=25, error_out=False))
#      return render_template('accountresults.html', pageid=pageid, page=page, pagination=pagination)
#   else:
#      return render_template('account.html', pageid=pageid)
#
#@api.route('/checkout/item', methods=['GET','POST'])
#def item(pageid="item"):
#   if request.method == 'POST':
#      if request.form['ItemNumber']:
#         ItemNumber = request.form['ItemNumber']
#      else:
#         ItemNumber = ""
#      if request.form['AccountNumber']:
#         AccountNumber = request.form['AccountNumber']
#      else:
#         AccountNumber = ""
#      if request.form['Description']:
#         Description = request.form['Description']
#      else:
#         Description = ""
#      if request.form['Page']:
#         if not request.form['Page'] == 'NaN':
#            page = int(request.form['Page'])
#         else:
#            page = 1
#      else:
#         page = 1
#      pagination = (Item.query
#         .filter(Item.ID.like("%s%s"%(ItemNumber,"%")))
#         .filter(Item.MemberNumber.like("%s%s"%(AccountNumber,"%")))
#         .filter(Item.Description.like("%s%s%s"%("%",Description,"%")))
#         .paginate(page=page, per_page=25, error_out=False))
#      return render_template('itemresults.html', pageid=pageid, page=page, pagination=pagination)
#   else:
#      return render_template('item.html', pageid=pageid)
#
#@api.route('/checkout')
#@api.route('/checkout/')
#@api.route('/checkout/<pageid>')
#def checkout(pageid=None):
#   return render_template('index.html', pageid=pageid)
#


