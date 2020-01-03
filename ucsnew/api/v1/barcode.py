from flask_restplus import Api, Resource, fields
from flask import send_file
from ... import http_auth

api = Api()
ns = api.namespace('barcodes', description="Generates barcodes")

from ...logic import generate_barcode

@ns.route('/<string:codedata>', endpoint='codedata')
@ns.param('codedata', description="Data to be encoded")
class Barcode(Resource):

    @http_auth.login_required
    @ns.doc('create_barcode')
    @ns.response(200, 'OK')
    @ns.response(403, 'Forbidden')
    @ns.response(404, 'Not Found')
    @ns.produces(['image/svg'])
    def get(self, codedata):

        '''Generate a barcode'''

        barcode_img = generate_barcode(codedata)

        return send_file(
            barcode_img,
            mimetype='image/svg',
            as_attachment=True,
            attachment_filename='{}.svg'.format(codedata)
            )
