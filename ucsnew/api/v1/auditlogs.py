from flask_restplus import Api
from flask_restplus import Resource
from flask_restplus import fields
from flask import g as flask_g
from ... import http_auth

api = Api()
ns = api.namespace('auditlogs', description="Audit Logs")

from .api_models import auditlog_model
auditlog_model = ns.model('AuditLog', auditlog_model)

from ...logic import get_auditlogs
from ...logic import create_auditlog

auditlog_parser = api.parser()
auditlog_parser.add_argument('auditlog_uuid', type=str, location='args',
        required=False, help='Query Audit Log UUID')
auditlog_parser.add_argument('username', type=str, location='args',
        required=False, help='Query User Logs')
auditlog_parser.add_argument('tag', type=str, location='args',
        required=False, help='Query Logs with tag')
auditlog_parser.add_argument('page', type=int, location='args',
        required=False, help='Page number')
auditlog_parser.add_argument('per_page', type=int, location='args',
        required=False, help='Results per page')

@ns.route('', methods=['GET','POST'])
class AuditLog(Resource):
    @http_auth.login_required
    @ns.doc('list_auditlogs')
    @ns.doc(parser=auditlog_parser, validate=True)
    @ns.marshal_with(auditlog_model, as_list=True)
    @ns.response(200, 'OK', model=auditlog_model)
    def get(self, auditlog_uuid=None, username=None, tag=None,
            page=1, per_page=25):

        '''List Audit Logs'''

        args = auditlog_parser.parse_args()
        results = get_auditlogs(
            args['auditlog_uuid'],
            args['username'],
            args['tag'],
            args['page'],
            args['per_page'],
        )

        return results, 200

    @http_auth.login_required
    @ns.doc('create_auditlog')
    @ns.doc(body=auditlog_model, validate=True)
    @ns.marshal_with(auditlog_model, code=201)
    @ns.response(201, 'Created', model=auditlog_model)
    @ns.response(403, 'Forbidden')
    def post(self):

        '''Create Audit Log'''

        return create_auditlog(flask_g.username, api.payload), 201


from .api_models import auditlogtag_model
auditlogtag_model = ns.model('AuditLogTag', auditlogtag_model)

from ...logic import get_auditlogtags

@ns.route('/<string:auditlog_uuid>/auditlogtags')
@ns.param('auditlog_uuid', description="Resource ID")
class AuditLogTags(Resource):

    @http_auth.login_required
    @ns.doc('list_tags')
    @ns.doc(body={}, validate=True)
    @ns.marshal_with(auditlogtag_model, as_list=True, code=200)
    @ns.response(200, 'OK', model=auditlogtag_model)
    @ns.response(404, 'Not Found')
    def get(self, auditlog_uuid):

        '''List tags from auditlog'''

        return get_auditlogtags(auditlog_uuid), 200
