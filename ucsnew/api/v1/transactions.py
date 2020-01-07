from flask_restplus import Api
from flask_restplus import Resource
from flask_restplus import fields
from flask import g as flask_g
from flask import send_file
from ... import http_auth

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
transaction_parser.add_argument('transaction_uuid', type=str, location='args',
        required=False, help='Query Transaction UUID')
transaction_parser.add_argument('page', type=int, location='args',
        required=False, help='Page number')
transaction_parser.add_argument('per_page', type=int, location='args',
        required=False, help='Results per page')

@ns.route('', methods=['GET','POST'])
class Transaction(Resource):
    @http_auth.login_required
    @ns.doc('list_transactions')
    @ns.doc(parser=transaction_parser, validate=True)
    @ns.marshal_with(transaction_model, as_list=True)
    @ns.response(200, 'OK', model=transaction_model)
    def get(self, username=None, itemnumber=None, transaction_uuid=None,
            page=1, per_page=25):

        '''List Transactions'''

        args = transaction_parser.parse_args()
        results = get_transactions(
            args['username'],
            args['itemnumber'],
            args['transaction_uuid'],
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

@ns.route('/<string:transaction_uuid>', endpoint='transaction')
@ns.param('transaction_uuid', description="Resource ID")
class TransactionResourceView(Resource):

    @http_auth.login_required
    @ns.doc('replace_transaction')
    @ns.doc(body=transaction_model, validate=True)
    @ns.marshal_with(transaction_model, code=200)
    @ns.response(200, 'OK', model=transaction_model)
    @ns.response(403, 'Forbidden')
    @ns.response(404, 'Not Found')
    def put(self, transaction_uuid):

        '''Replace transaction'''

        return replace_transaction(flask_g.username, transaction_uuid,
                api.payload), 200

    @http_auth.login_required
    @ns.doc('patch_transaction')
    @ns.doc(body=transaction_model, validate=True)
    @ns.marshal_with(transaction_model, code=200)
    @ns.response(200, 'OK', model=transaction_model)
    @ns.response(403, 'Forbidden')
    @ns.response(404, 'Not Found')
    def patch(self, transaction_uuid):

        '''Patch transaction'''

        return patch_transaction(flask_g.username, transaction_uuid,
                api.payload), 200

    @http_auth.login_required
    @ns.doc('delete_transaction')
    @ns.doc(body=delete_transaction_model, validate=True)
    @ns.marshal_with(delete_transaction_model, code=200)
    @ns.response(200, 'OK', model=delete_transaction_model)
    @ns.response(403, 'Forbidden')
    @ns.response(404, 'Not Found')
    def delete(self, transaction_uuid):

        '''Delete transaction'''

        return delete_transaction(flask_g.username, transaction_uuid, api.payload), 200


from .api_models import delete_item_model
from .api_models import item_model
item_model = ns.model('Item', item_model)

from ...logic import listitemfrom_transaction
from ...logic import additemto_transaction
from ...logic import removeitemfrom_transaction
from ...logic import generate_transaction_pdf

@ns.route('/<string:transaction_uuid>/items')
@ns.param('transaction_uuid', description="Resource ID")
class TransactionItems(Resource):

    @http_auth.login_required
    @ns.doc('list_items')
    @ns.doc(body=delete_item_model, validate=True)
    @ns.marshal_with(item_model, as_list=True, code=200)
    @ns.response(200, 'OK', model=item_model)
    @ns.response(404, 'Not Found')
    def get(self, transaction_uuid):

        '''List items from transaction'''

        return listitemfrom_transaction(transaction_uuid), 200

@ns.route('/<string:transaction_uuid>/pdf')
@ns.param('transaction_uuid', description="Resource ID")
class TransactionPDF(Resource):

    @http_auth.login_required
    @ns.doc('create_pdf')
    @ns.response(200, 'OK')
    @ns.response(404, 'Not Found')
    @ns.produces(['application/pdf'])
    def get(self, transaction_uuid):

        '''Generates a PDF receipt'''

        transaction_pdf = generate_transaction_pdf(transaction_uuid)

        return send_file(
                transaction_pdf,
                mimetype='application/pdf',
                as_attachment=True,
                attachment_filename='{}.pdf'.format(transaction_uuid),
                cache_timeout=0,
                )


@ns.route('/<string:transaction_uuid>/items/<string:item_uuid>',
        endpoint='transaction_items')
@ns.param('transaction_uuid', description="Resource ID")
@ns.param('item_uuid', description="Resource ID")
class TransactionItemsResourceView(Resource):

    @http_auth.login_required
    @ns.doc('create_item')
    @ns.doc(body=delete_item_model, validate=True)
    @ns.marshal_with(item_model, as_list=True, code=201)
    @ns.response(201, 'Created', model=item_model)
    @ns.response(403, 'Forbidden')
    @ns.response(404, 'Not Found')
    def post(self, transaction_uuid, item_uuid):

        '''Add item to transaction'''

        return additemto_transaction(flask_g.username, transaction_uuid,
                item_uuid), 201

    @http_auth.login_required
    @ns.doc('delete_item')
    @ns.doc(body=delete_item_model, validate=True)
    @ns.marshal_with(item_model, as_list=True, code=200)
    @ns.response(200, 'OK', model=item_model)
    @ns.response(403, 'Forbidden')
    @ns.response(404, 'Not Found')
    def delete(self, transaction_uuid, item_uuid):

        '''Remove item from transaction'''

        return removeitemfrom_transaction(flask_g.username, transaction_uuid,
                item_uuid), 200
