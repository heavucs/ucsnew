from flask_restplus import Namespace, Resource, fields
from ucsnew.core.logic import *

# For debug purposes (app.logger)
from ucsnew.application import app

api = Namespace('Checkout', Description='Checkout related functions')

from .api_models import account_model, item_model
account = api.model('Account', account_model)
item = api.model('Item', item_model)

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

