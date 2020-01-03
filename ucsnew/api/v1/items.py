from flask_restplus import Api, Resource, fields
from flask import g as flask_g
from ... import http_auth

api = Api()
ns = api.namespace('items', description="Items for sale")

from .api_models import item_model
from .api_models import delete_item_model
item_model = ns.model('Item', item_model)

from ...logic import get_items
from ...logic import create_item
from ...logic import replace_item
from ...logic import patch_item
from ...logic import delete_item

item_parser = api.parser()
item_parser.add_argument('item_uuid', type=str, location='args',
        required=False, help='Query Item UUID')
item_parser.add_argument('membernumber', type=str, location='args',
        required=False, help='Query Account Number')
item_parser.add_argument('description', type=str, location='args',
        required=False, help='Query Description')
item_parser.add_argument('transaction_uuid', type=str, location='args',
        required=False, help='Query Transaction UUID')
item_parser.add_argument('page', type=int, location='args',
        required=False, help='Page number')
item_parser.add_argument('per_page', type=int, location='args',
        required=False, help='Results per page')

@ns.route('', methods=['GET','POST'])
class Item(Resource):
    @http_auth.login_required
    @ns.doc('list_items')
    @ns.doc(parser=item_parser, validate=True)
    @ns.marshal_with(item_model, as_list=True)
    @ns.response(200, 'OK', model=item_model)
    def get(self, item_uuid=None, membernumber=None, description=None,
            transaction_uuid=None, page=1, per_page=25):

        '''List Items'''

        args = item_parser.parse_args()
        results = get_items(
            args['item_uuid'],
            args['membernumber'],
            args['description'],
            args['transaction_uuid'],
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

        return create_item(flask_g.username, api.payload), 201

@ns.route('/<string:uuid>', endpoint='item')
@ns.param('uuid', description="Resource ID")
class ItemResourceView(Resource):

    @http_auth.login_required
    @ns.doc('replace_item')
    @ns.doc(body=item_model, validate=True)
    @ns.marshal_with(item_model, code=200)
    @ns.response(200, 'OK', model=item_model)
    @ns.response(403, 'Forbidden')
    @ns.response(404, 'Not Found')
    def put(self, uuid):

        '''Replace item'''

        return replace_item(flask_g.username, uuid, api.payload), 200

    @http_auth.login_required
    @ns.doc('patch_item')
    @ns.doc(body=item_model, validate=True)
    @ns.marshal_with(item_model, code=200)
    @ns.response(200, 'OK', model=item_model)
    @ns.response(403, 'Forbidden')
    @ns.response(404, 'Not Found')
    def patch(self, uuid):

        '''Patch item'''

        return patch_item(flask_g.username, uuid, api.payload), 200

    @http_auth.login_required
    @ns.doc('delete_item')
    @ns.doc(body=delete_item_model, validate=True)
    @ns.marshal_with(delete_item_model, code=200)
    @ns.response(200, 'OK', model=delete_item_model)
    @ns.response(403, 'Forbidden')
    @ns.response(404, 'Not Found')
    def delete(self, uuid):

        '''Delete item'''

        return delete_item(flask_g.username, uuid, api.payload), 200
