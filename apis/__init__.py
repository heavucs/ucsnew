from flask_restplus import Api
from checkoutapi import ns as checkoutapi

api = Api(
   title='Checkout',
   version='1.0',
   description='checkout api',
)

api.add_namespace(checkoutapi, path="/checkoutapi")


