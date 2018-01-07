from flask_restplus import Api, Resource, fields
from ..application import http_auth

api = Api()
ns = api.namespace('items', description="Items for sale")

from .api_models import item_model
item_model = ns.model('Item', item_model)

from ..logic import get_items_list, create_item

item_parser = api.parser()
item_parser.add_argument('itemnumber', type=str, location='args', required=False, help='Query Item Number')
item_parser.add_argument('membernumber', type=str, location='args', required=False, help='Query Account Number')
item_parser.add_argument('description', type=str, location='args', required=False, help='Query Description')
item_parser.add_argument('page', type=int, location='args', required=False, help='Page number')
item_parser.add_argument('per_page', type=int, location='args', required=False, help='Results per page')

@ns.route('', methods=['GET','POST'])
class Item(Resource):
    @http_auth.login_required
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

    @http_auth.login_required
    @ns.doc('create_item')
    @ns.doc(body=item_model, validate=True)
    @ns.marshal_with(item_model, code=201)
    @ns.response(201, 'Created', model=item_model)
    @ns.response(403, 'Forbidden')
    def post(self):
        '''Create Item'''
        return create_item(api.payload), 201

