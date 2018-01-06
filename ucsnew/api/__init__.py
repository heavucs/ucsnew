from flask import Blueprint
from flask_restplus import Api

api = Api()

from .items import ns as ns_items
api.add_namespace(ns_items, path='/items')
from .members import ns as ns_members
api.add_namespace(ns_members, path='/members')
