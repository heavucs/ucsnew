from flask_restplus import Namespace, Resource, fields, Api
from ucsnew.core.logic import *

# For debug purposes (app.logger)
from ucsnew.application import app

api = Api()
ns = Namespace('Checkout', Description='Checkout related functions')

from .api_models import item_model, account_model
item_model = ns.model('Item', item_model)
account_model = ns.model('Account', account_model)

#class GenericView(Resource):
#   pass

@ns.route('/items', methods=['GET','POST'])
class Item(Resource):
   @ns.doc('create_item')
   @ns.doc(body=item_model)
   @ns.expect(item_model, validate=True)
   @ns.marshal_with(item_model)
   @ns.response(200, 'OK', model=item_model)
   @ns.response(201, 'Created', model=item_model)
   @ns.response(403, 'Forbidden')
   def post(self):
      '''Create Item'''
      return create_item(api.payload), 201

   @ns.doc(params={
      'query_itemnumber': 'Query Item Number',
      'query_membernumber': 'Query Account Number',
      'query_description': 'Query Description',
      'page': 'Page number',
      'per_page': 'Results per page',
      })
   @ns.doc('list_items')
   @ns.marshal_list_with(item_model)
   @ns.response(200, 'OK', model=item_model)
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


@ns.route('/accounts', methods=['GET'])
@ns.doc(params={
   'query_memberid': 'Query member\'s database ID',
   'query_membernumber': 'Query Member Number',
   'query_lastname': 'Query Member\'s last name',
   'query_phonenumber': 'Query Member\'s phone number',
   'page': 'Page number',
   'per_page': 'Results per page',
   })
class AccountList(Resource):
   @ns.doc('list_Accounts')
   @ns.marshal_list_with(account_model)
   @ns.response(200, 'OK', model=account_model)
   def get(self, query_memberid=None, query_membernumber=None, query_lastname=None, query_phonenumber=None, page=1, per_page=25):
      '''List Accounts'''

      parser = ns.parser()

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


