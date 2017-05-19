from flask_restplus import Api
from checkoutapi import api as checkoutapi

api = Api(
   title='checkout',
   version='1.0',
   description='checkout application',
)

#api.add_namespace(checkout, path="/checkout")
api.add_namespace(checkoutapi, path="/checkoutapi")

