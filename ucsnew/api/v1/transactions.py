from flask_restplus import Api, Resource, fields
from flask import g as flask_g
from ...application import http_auth

api = Api()
ns = api.namespace('transactions', description="Sales transactions")

from .api_models import transaction_model
from .api_models import delete_transaction_model
transaction_model = ns.model('Transaction', transaction_model)

from ...logic import get_transactions
from ...logic import create_transaction
from ...logic import replace_transaction
from ...logic import patch_transaction
from ...logic import delete_transaction

transaction_parser = api.parser()
transaction_parser.add_argument('username', type=str, location='args',
        required=False, help='Query User Transactions')
transaction_parser.add_argument('itemnumber', type=str, location='args',
        required=False, help='Query Transactions by itemnumber')
transaction_parser.add_argument('transactionnumber', type=str, location='args',
        required=False, help='Query Transaction Number')
transaction_parser.add_argument('page', type=int, location='args',
        required=False, help='Page number')
transaction_parser.add_argument('per_page', type=int, location='args',
        required=False, help='Results per page')

@ns.route('/', methods=['GET','POST'])
class Transaction(Resource):
    @http_auth.login_required
    @ns.doc('list_transactions')
    @ns.doc(parser=transaction_parser, validate=True)
    @ns.marshal_with(transaction_model, as_list=True)
    @ns.response(200, 'OK', model=transaction_model)
    def get(self, username=None, itemnumber=None, transactionnumber=None,
            page=1, per_page=25):

        '''List Transactions'''

        args = transaction_parser.parse_args()
        results = get_transactions_list(
            args['username'],
            args['itemnumber'],
            args['transactionnumber'],
            args['page'],
            args['per_page'],
        )

        return results, 200

    @http_auth.login_required
    @ns.doc('create_transaction')
    @ns.doc(body=transaction_model, validate=True)
    @ns.marshal_with(transaction_model, code=201)
    @ns.response(201, 'Created', model=transaction_model)
    @ns.response(403, 'Forbidden')
    def post(self):

        '''Create Transaction'''

        return create_transaction(flask_g.username, api.payload), 201

@ns.route('/<string:uuid>', endpoint='transaction')
@ns.param('uuid', description="Resource ID")
class TransactionResourceView(Resource):

    @http_auth.login_required
    @ns.doc('replace_transaction')
    @ns.doc(body=transaction_model, validate=True)
    @ns.marshal_with(transaction_model, code=200)
    @ns.response(200, 'OK', model=transaction_model)
    @ns.response(403, 'Forbidden')
    @ns.response(404, 'Not Found')
    def put(self, uuid):

        '''Replace transaction'''

        return replace_transaction(flask_g.username, uuid, api.payload), 200

    @http_auth.login_required
    @ns.doc('patch_transaction')
    @ns.doc(body=transaction_model, validate=True)
    @ns.marshal_with(transaction_model, code=200)
    @ns.response(200, 'OK', model=transaction_model)
    @ns.response(403, 'Forbidden')
    @ns.response(404, 'Not Found')
    def patch(self, uuid):

        '''Patch transaction'''

        return patch_transaction(flask_g.username, uuid, api.payload), 200

    @http_auth.login_required
    @ns.doc('delete_transaction')
    @ns.doc(body=delete_transaction_model, validate=True)
    @ns.marshal_with(delete_transaction_model, code=200)
    @ns.response(200, 'OK', model=delete_transaction_model)
    @ns.response(403, 'Forbidden')
    @ns.response(404, 'Not Found')
    def delete(self, uuid):

        '''Delete transaction'''

        return delete_transaction(flask_g.username, uuid, api.payload), 200
