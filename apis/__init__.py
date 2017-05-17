from flask_restplus import Api

from checkout import api as checkout

api = Api(
   title='checkout',
   version='1.0',
   description='checkout application',
)

#api.add_namespace(checkout, path="/checkout")
api.add_namespace(checkout)

