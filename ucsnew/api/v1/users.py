from flask_restplus import Api, Resource, fields
from flask import g as flask_g
from ...application import http_auth

api = Api()
ns = api.namespace('users', description="Users of this application")

from .api_models import user_model
from .api_models import delete_user_model
user_model = ns.model('User', user_model)

from ...logic import get_users
from ...logic import create_user
from ...logic import replace_user
from ...logic import patch_user
from ...logic import delete_user

user_parser = ns.parser()
user_parser.add_argument('username', type=str, location='args',
        required=False, help='Query User\'s username')
user_parser.add_argument('firstname', type=str, location='args',
        required=False, help='Query User\'s first name')
user_parser.add_argument('lastname', type=str, location='args',
        required=False, help='Query User\'s last name')
user_parser.add_argument('page', type=int, location='args',
        required=False, help='Page number')
user_parser.add_argument('per_page', type=int, location='args',
        required=False, help='Results per page')

@ns.route('/', methods=['GET','POST'])
class User(Resource):

    @http_auth.login_required
    @ns.doc('list_users')
    @ns.doc(parser=user_parser)
    @ns.marshal_with(user_model, as_list=True)
    @ns.response(200, 'OK', model=user_model)
    def get(self, q_username=None, q_firstname=None, q_lastname=None,
            page=1, per_page=25):

        '''List users'''

        args = user_parser.parse_args()
        results = get_users(
            args['page'],
            args['per_page'],
        )

        return results, 200

    @http_auth.login_required
    @ns.doc('create_user')
    @ns.doc(body=user_model, validate=True)
    @ns.marshal_with(user_model, code=201)
    @ns.response(201, 'Created', model=user_model)
    @ns.response(403, 'Forbidden')
    def post(self):

        '''Create user'''

        return create_user(api.payload), 201

@ns.route('/<string:username>', endpoint='user')
@ns.param('username', description="Resource ID")
class UserResourceView(Resource):

    @http_auth.login_required
    @ns.doc('replace_user')
    @ns.doc(body=user_model, validate=True)
    @ns.marshal_with(user_model, code=200)
    @ns.response(200, 'OK', model=user_model)
    @ns.response(403, 'Forbidden')
    @ns.response(404, 'Not Found')
    def put(self, username):

        '''Replace user'''

        return replace_user(flask_g.username, username, api.payload), 200

    @http_auth.login_required
    @ns.doc('patch_user')
    @ns.doc(body=user_model, validate=True)
    @ns.marshal_with(user_model, code=200)
    @ns.response(200, 'OK', model=user_model)
    @ns.response(403, 'Forbidden')
    @ns.response(404, 'Not Found')
    def patch(self, username):

        '''Patch user'''

        return patch_user(flask_g.username, username, api.payload), 200

    @http_auth.login_required
    @ns.doc('delete_user')
    @ns.doc(body=delete_user_model, validate=True)
    @ns.marshal_with(delete_user_model, code=200)
    @ns.response(200, 'OK', model=delete_user_model)
    @ns.response(403, 'Forbidden')
    @ns.response(404, 'Not Found')
    def delete(self, username):

        '''Delete user'''

        return delete_user(flask_g.username, username, api.payload), 200
