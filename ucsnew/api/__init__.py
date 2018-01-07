from flask import Blueprint
from flask_restplus import Api

api = Api()

from .members import ns as ns_members
api.add_namespace(ns_members, path='/members')
from .items import ns as ns_items
api.add_namespace(ns_items, path='/items')
from .users import ns as ns_users
api.add_namespace(ns_users, path='/users')
