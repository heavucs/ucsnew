from flask_restplus import Api, Resource, fields
from ...application import http_auth

api = Api()
ns = api.namespace('transactions', description="Transactions for sale")

from .api_models import transaction_model
transaction_model = ns.model('Transaction', transaction_model)

from ...logic import get_transactions_list

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

@ns.route('', methods=['GET','POST'])
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
