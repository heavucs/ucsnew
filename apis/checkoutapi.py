from flask_restplus import Namespace, Resource, fields, Api
from ucsnew.core.logic import *

# For debug purposes (app.logger)
from ucsnew.application import app

api = Api()
ns = Namespace('Checkout', Description='Checkout related functions')

from .api_models import item_model, account_model
item_model = ns.model('Item', item_model)
account_model = ns.model('Account', account_model)

item_parser = api.parser()
item_parser.add_argument('itemnumber', type=str, location='args', required=False, help='Query Item Number')
item_parser.add_argument('membernumber', type=str, location='args', required=False, help='Query Account Number')
item_parser.add_argument('description', type=str, location='args', required=False, help='Query Description')
item_parser.add_argument('page', type=int, location='args', required=False, help='Page number')
item_parser.add_argument('per_page', type=int, location='args', required=False, help='Results per page')

account_parser = ns.parser()
account_parser.add_argument('memberid', type=int, location='args', required=False, help='Query member\'s database ID')
account_parser.add_argument('membernumber', type=str, location='args', required=False, help='Query Member Number')
account_parser.add_argument('lastname', type=str, location='args', required=False, help='Query Member\'s last name')
account_parser.add_argument('phone', type=str, location='args', required=False, help='Query Member\'s phone number')
account_parser.add_argument('page', type=int, location='args', required=False, help='Page number')
account_parser.add_argument('per_page', type=int, location='args', required=False, help='Results per page')

@ns.route('/items', methods=['GET','POST'])
class Item(Resource):
   @ns.doc('list_items')
   @ns.doc(parser=item_parser, validate=True)
   @ns.marshal_with(item_model, as_list=True)
   @ns.response(200, 'OK', model=item_model)
   def get(self, itemnumber=None, membernumber=None, description=None, page=1, per_page=25):
      '''List Items'''

      args = item_parser.parse_args()
      results = get_items_list(
         args['itemnumber'],
         args['membernumber'],
         args['description'],
         args['page'],
         args['per_page'],
      )

      return results, 200

   @ns.doc('create_item')
   @ns.doc(body=item_model, validate=True)
   @ns.marshal_with(item_model, code=201)
   @ns.response(201, 'Created', model=item_model)
   @ns.response(403, 'Forbidden')
   def post(self):
      '''Create Item'''
      return create_item(api.payload), 201


@ns.route('/accounts', methods=['GET','POST'])
class AccountList(Resource):
   @ns.doc('list_Accounts')
   @ns.doc(parser=account_parser)
   @ns.marshal_with(account_model, as_list=True)
   @ns.response(200, 'OK', model=account_model)
   def get(self, memberid=None, membernumber=None, lastname=None, phone=None, page=1, per_page=25):
      '''List Accounts'''

      args = account_parser.parse_args()
      results = get_accounts_list(
         args['memberid'],
         args['membernumber'],
         args['lastname'],
         args['phone'],
         args['page'],
         args['per_page'],
      )

      return results, 200

   @ns.doc('create_account')
   @ns.doc(body=account_model, validate=True)
   @ns.marshal_with(account_model, code=201)
   @ns.response(201, 'Created', model=account_model)
   @ns.response(403, 'Forbidden')
   def post(self):
      '''Create Account'''
      return create_account(api.payload), 201


