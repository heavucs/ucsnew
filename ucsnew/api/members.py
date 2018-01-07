from flask_restplus import Api, Resource, fields
from ..application import http_auth

api = Api()
ns = api.namespace('members', description="Members who are selling items")

from .api_models import member_model
member_model = ns.model('Member', member_model)

from ..logic import get_members_list, create_member

member_parser = ns.parser()
member_parser.add_argument('memberid', type=int, location='args', required=False, help='Query member\'s database ID')
member_parser.add_argument('membernumber', type=str, location='args', required=False, help='Query Member Number')
member_parser.add_argument('lastname', type=str, location='args', required=False, help='Query Member\'s last name')
member_parser.add_argument('phone', type=str, location='args', required=False, help='Query Member\'s phone number')
member_parser.add_argument('page', type=int, location='args', required=False, help='Page number')
member_parser.add_argument('per_page', type=int, location='args', required=False, help='Results per page')

@ns.route('/', methods=['GET','POST'])
class Member(Resource):
    @http_auth.login_required
    @ns.doc('list_members')
    @ns.doc(parser=member_parser)
    @ns.marshal_with(member_model, as_list=True)
    @ns.response(200, 'OK', model=member_model)
    def get(self, memberid=None, membernumber=None, lastname=None, phone=None, page=1, per_page=25):
        '''List Members'''

        args = member_parser.parse_args()
        results = get_members_list(
            args['memberid'],
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

