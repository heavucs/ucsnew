from flask import Blueprint
from flask_restplus import Api

api = Api()

from .members import ns as ns_members
api.add_namespace(ns_members, path='/api/1.0/members')
from .items import ns as ns_items
api.add_namespace(ns_items, path='/api/1.0/items')
from .transactions import ns as ns_transactions
api.add_namespace(ns_transactions, path='/api/1.0/transactions')
from .users import ns as ns_users
api.add_namespace(ns_users, path='/api/1.0/users')
from .barcode import ns as ns_barcode
api.add_namespace(ns_barcode, path='/api/1.0/barcode')
