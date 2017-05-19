from flask_restplus import fields

item_model = {
#item = api.model('Item', {
   'ID': fields.String(readOnly=True, description='AutoIncremented ID'),
   'MemberNumber': fields.String(required=True, description='Account Number'),
   'ItemNumber': fields.String(required=True, description='ItemNumber within account'),
   'Description': fields.String(required=True, description='Description of the item'),
   'Category': fields.String(Required=True, description='Item\'s Category'),
   'NumItems': fields.Integer(Required=True, description='Number of items included in "Item" e.g. a set of books'),
   'Status': fields.Integer(Required=True, description='Represents Item status, 0 not checked-in, 1 checked-in, 2 sold'),
   'FridayPrice': fields.Float(Required=True, description='Friday price', min=1.00, example='1.00'),
   'SaturdayPrice': fields.Float(Required=True, description='Saturday price', min=1.00, example='1.00'),
}

account_model = {
#account = api.model('Account', {
   'ID': fields.Integer(readOnly=True, description='AutoIncremented ID'),
   'MemberNumber': fields.String(required=True, description='Account Number'),
   'FirstName': fields.String(required=True, description='First name associated with Account'),
   'LastName': fields.String(required=True, description='Last name associated with Account'),
   'Items': fields.Integer(Required=True, description='Number of items associated with Account'),
   'Activated': fields.DateTime(Required=True, description='Date Account was activated'),
   'Phone': fields.String(required=True, description='Contact number'),
}

