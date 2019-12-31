from flask_restplus import Api, Resource, fields
from flask import g as flask_g
from ...application import http_auth

api = Api()
ns = api.namespace('members', description="Members who are selling items")

from .api_models import member_model
from .api_models import delete_member_model
member_model = ns.model('Member', member_model)

from ...logic import get_members
from ...logic import create_member
from ...logic import replace_member
from ...logic import patch_member
from ...logic import delete_member

member_parser = ns.parser()
member_parser.add_argument('membernumber', type=str, location='args',
        required=False, help='Query Member Number')
member_parser.add_argument('lastname', type=str, location='args',
        required=False, help='Query Member\'s last name')
member_parser.add_argument('phone', type=str, location='args',
        required=False, help='Query Member\'s phone number')
member_parser.add_argument('page', type=int, location='args',
        required=False, help='Page number')
member_parser.add_argument('per_page', type=int, location='args',
        required=False, help='Results per page')

@ns.route('/', methods=['GET','POST'])
class Member(Resource):
    @http_auth.login_required
    @ns.doc('list_members')
    @ns.doc(parser=member_parser)
    @ns.marshal_with(member_model, as_list=True)
    @ns.response(200, 'OK', model=member_model)
    def get(self, membernumber=None, lastname=None, phone=None,
            page=1, per_page=25):

        '''List Members'''

        args = member_parser.parse_args()
        results = get_members(
            args['membernumber'],
            args['lastname'],
            args['phone'],
            args['page'],
            args['per_page'],
        )

        return results, 200

    @http_auth.login_required
    @ns.doc('create_member')
    @ns.doc(body=member_model, validate=True)
    @ns.marshal_with(member_model, code=201)
    @ns.response(201, 'Created', model=member_model)
    @ns.response(403, 'Forbidden')
    def post(self):

        '''Create Member'''

        return create_member(api.payload), 201

@ns.route('/<string:membernumber>', endpoint='member')
@ns.param('membernumber', description="Resource ID")
class MemberResourceView(Resource):

    @http_auth.login_required
    @ns.doc('replace_member')
    @ns.doc(body=member_model, validate=True)
    @ns.marshal_with(member_model, code=200)
    @ns.response(200, 'OK', model=member_model)
    @ns.response(403, 'Forbidden')
    @ns.response(404, 'Not Found')
    def put(self, membernumber):

        '''Replace member'''

        return replace_member(flask_g.username, membernumber, api.payload), 200

    @http_auth.login_required
    @ns.doc('patch_member')
    @ns.doc(body=member_model, validate=True)
    @ns.marshal_with(member_model, code=200)
    @ns.response(200, 'OK', model=member_model)
    @ns.response(403, 'Forbidden')
    @ns.response(404, 'Not Found')
    def patch(self, membernumber):

        '''Patch member'''

        return patch_member(flask_g.username, membernumber, api.payload), 200

    @http_auth.login_required
    @ns.doc('delete_member')
    @ns.doc(body=delete_member_model, validate=True)
    @ns.marshal_with(delete_member_model, code=200)
    @ns.response(200, 'OK', model=delete_member_model)
    @ns.response(403, 'Forbidden')
    @ns.response(404, 'Not Found')
    def delete(self, membernumber):

        '''Delete member'''

        return delete_member(flask_g.username, membernumber, api.payload), 200
