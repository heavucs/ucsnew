from flask_restplus import Namespace, Resource, fields
from ucsnew.core.logic import *

# For debug purposes (app.logger)
from ucsnew.application import app

api = Namespace('Checkout', Description='Checkout related functions')

item = api.model('Item', {
   'ID': fields.String(readOnly=True, description='AutoIncremented ID'),
   'MemberNumber': fields.String(required=True, description='Account Number'),
   'ItemNumber': fields.String(required=True, description='ItemNumber within account'),
   'Description': fields.String(required=True, description='Description of the item'),
   'Category': fields.String(Required=True, description='Item\'s Category'),
   'NumItems': fields.Integer(Required=True, description='Number of items included in "Item" e.g. a set of books'),
   'Status': fields.Integer(Required=True, description='Represents Item status, 0 not checked-in, 1 checked-in, 2 sold'),
   'FridayPrice': fields.Float(Required=True, description='Friday price', min=1.00, example='1.00'),
   'SaturdayPrice': fields.Float(Required=True, description='Saturday price', min=1.00, example='1.00'),
})

account = api.model('Account', {
   'ID': fields.Integer(readOnly=True, description='AutoIncremented ID'),
   'MemberNumber': fields.String(required=True, description='Account Number'),
   'FirstName': fields.String(required=True, description='First name associated with Account'),
   'LastName': fields.String(required=True, description='Last name associated with Account'),
   'Items': fields.Integer(Required=True, description='Number of items associated with Account'),
   'Activated': fields.DateTime(Required=True, description='Date Account was activated'),
   'Phone': fields.String(required=True, description='Contact number'),
})

@api.route('/items', methods=['GET'])
@api.doc(params={
   'query_itemnumber': 'Query Item Number',
   'query_membernumber': 'Query Account Number',
   'query_description': 'Query Description',
   'page': 'Page number',
   'per_page': 'Results per page',
   })
class ItemList(Resource):
   @api.doc('list_items')
   @api.marshal_list_with(item)
   @api.response(200, 'OK', model=item)
   def get(self, query_itemnumber=None, query_membernumber=None, query_description=None, page=1, per_page=25):
      '''List Items'''

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


@api.route('/accounts', methods=['GET'])
@api.doc(params={
   'query_memberid': 'Query member\'s database ID',
   'query_membernumber': 'Query Member Number',
   'query_lastname': 'Query Member\'s last name',
   'query_phonenumber': 'Query Member\'s phone number',
   'page': 'Page number',
   'per_page': 'Results per page',
   })
class ItemList(Resource):
   @api.doc('list_Accounts')
   @api.marshal_list_with(account)
   @api.response(200, 'OK', model=account)
   def get(self, query_memberid=None, query_membernumber=None, query_lastname=None, query_phonenumber=None, page=1, per_page=25):
      '''List accounts'''

      parser = api.parser()

      parser.add_argument('query_memberid', type=int, location='args')
      parser.add_argument('query_membernumber', type=str, location='args')
      parser.add_argument('query_lastname', type=str, location='args')
      parser.add_argument('query_phonenumber', type=str, location='args')
      parser.add_argument('page', type=int, location='args')
      parser.add_argument('per_page', type=int, location='args')
      
      args = parser.parse_args()

      results = get_accounts_list(
         args['query_memberid'],
         args['query_membernumber'],
         args['query_lastname'],
         args['query_phonenumber'],
         args['page'],
         args['per_page'],
      )

      return results, 200

