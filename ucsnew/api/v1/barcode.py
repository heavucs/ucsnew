from flask_restplus import Api, Resource, fields
from flask import send_file
from ...application import http_auth

api = Api()
ns = api.namespace('barcodes', description="Generates barcodes")

from ...logic import get_barcodes_list, create_barcode

@ns.route('/<string:barcode_number>', endpoint='code')
@ns.param('barcode_number', description="Resource ID")
class Barcode(Resource):

    @http_auth.login_required
    @ns.doc('create_barcode')
    @ns.response(200, 'OK')
    @ns.response(403, 'Forbidden')
    @ns.response(404, 'Not Found')
    @ns.produces(['image/svg'])
    def get(self, barcode_number):

        '''Generate a barcode'''

        barcode_img = create_barcode(barcode_number)

        return send_file(
            barcode_img,
            mimetype='image/svg',
            as_attachment=True,
            attachment_filename='{}.svg'.format(barcode_number)
            )
