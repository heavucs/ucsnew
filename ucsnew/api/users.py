from flask_restplus import Api, Resource, fields
from flask import g as flask_g
from ..application import http_auth

api = Api()
ns = api.namespace('users', description="Users of this application")

from .api_models import user_model, delete_user_model
user_model = ns.model('User', user_model)
#delete_user_model = ns.model('User', delete_user_model)

from ..logic import get_users_list, create_user
from ..logic import get_user, replace_user, delete_user

@ns.route('/', methods=['GET','POST'])
class UserListView(Resource):

    @http_auth.login_required
    @ns.doc('list_users')
    @ns.marshal_with(user_model, as_list=True)
    @ns.response(200, 'OK', model=user_model)
    def get(self):

        '''List users'''

        return get_users_list(), 200

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
    @ns.doc('get_user')
    @ns.marshal_with(user_model, code=200)
    @ns.response(200, 'OK', model=user_model)
    @ns.response(403, 'Forbidden')
    @ns.response(404, 'Not Found')
    def put(self, username):

        '''Get a single user'''

        return get_user(username), 200

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
    @ns.doc('delete_user')
    @ns.doc(body=delete_user_model, validate=True)
    @ns.marshal_with(delete_user_model, code=200)
    @ns.response(200, 'OK', model=delete_user_model)
    @ns.response(403, 'Forbidden')
    @ns.response(404, 'Not Found')
    def delete(self, username):

        '''Delete user'''

        return delete_user(flask_g.username, username, api.payload), 200

