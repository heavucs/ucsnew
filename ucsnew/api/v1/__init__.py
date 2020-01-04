from flask_restplus import Api
from flask import Blueprint

blueprint = Blueprint('api_v1', __name__, url_prefix='/api/1.0')
api = Api(blueprint,
        title='UCS API',
        version='1.0',
        description='Core UCS Application API',
        )

from .members import ns as ns_members
api.add_namespace(ns_members, path='')
from .items import ns as ns_items
api.add_namespace(ns_items, path='')
from .transactions import ns as ns_transactions
api.add_namespace(ns_transactions, path='')
from .users import ns as ns_users
api.add_namespace(ns_users, path='')
from .barcode import ns as ns_barcode
api.add_namespace(ns_barcode, path='')
from .auditlogs import ns as ns_auditlogs
api.add_namespace(ns_auditlogs, path='')
