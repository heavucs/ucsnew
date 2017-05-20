from flask_restplus import fields

RE_PHONENUMBER = r'^[0-9]{10}$'

item_model = {
   'ID': fields.String(readOnly=True, description='AutoIncremented ID'),
   'ItemNumber': fields.String(readOnly=True, description='ItemNumber within Account'),
   'MemberNumber': fields.String(required=True, description='Account Number'),
   'Description': fields.String(required=True, description='Description of the item'),
   'Category': fields.String(required=True, description='Item\'s Category'),
   'Subject': fields.String(required=True, description='School subject'),
   'Publisher': fields.String(required=False, description='Book Publisher'),
   'Year': fields.String(required=False, description='Published Year'),
   'ISBN': fields.String(required=False, description='Book\'s ISBN number'),
   'Condition': fields.Integer(required=False, description='0:Poor,1:BelowAverage,2:Average,3:Good,4:New', example=4, min=0, max=4),
   'ConditionDetail': fields.String(required=False, description='Additional comments on condition'),
   #'NumItems': fields.Integer(required=True, description='Number of items included in "Item" e.g. a set of books', example=1, min=1),
   'FridayPrice': fields.Float(required=True, description='Friday price', min=1.00, example=1.00),
   'SaturdayPrice': fields.Float(required=True, description='Saturday price', min=1.00, example=1.00),
   'Donate': fields.Integer(required=True, description='0:False,1:True', min=0, max=1, example=0),
   'CheckedIn': fields.DateTime(required=False, description='The presense of a datetime indicates checkedin'),
   'CheckedOut': fields.DateTime(required=False, description='The presense of a datetime indicates sold'),
   'Status': fields.Integer(required=True, description='0:Pending,1:CheckedIn,2:Sold,3:PickedUp,4:Deleted', example=0, min=0, max=4),
   'Deleted': fields.Integer(required=False, description='0:False,1:True', min=0, max=1, example=0),
   'Printed': fields.Integer(required=False, description='0:False,1:True', min=0, max=1, example=0),
}

account_model = {
   'ID': fields.Integer(readOnly=True, description='AutoIncremented ID'),
   'MemberNumber': fields.String(required=True, description='Account Number'),
   'Established': fields.DateTime(required=True, description='DateTime account was created'),
   'FirstName': fields.String(required=True, description='First name associated with Account'),
   'LastName': fields.String(required=True, description='Last name associated with Account'),
   'Address': fields.String(required=True, description='Mailing address 1'),
   'Address2': fields.String(required=True, description='Mailing address 2'),
   'City': fields.String(required=True, description='Mailing city'),
   'State': fields.String(required=True, description='Mailing state'),
   'Zip': fields.String(required=True, description='Mailing zip'),
   'Phone': fields.String(required=True, description='Contact number', example='1231231234', pattern=RE_PHONENUMBER),
   'Email': fields.String(required=True, descrpition='Contact e-mail'),
   'Password': fields.String(required=True, description='Account password'),
   'Question': fields.String(required=True, description='Secret question for password retrieval'),
   'Answer': fields.String(required=True, description='Secret answer for secret question'),
   'ActivationCode': fields.String(required=True, description='Activation code'),
   'Activated': fields.DateTime(required=True, description='DateTime Account was activated'),
   'Admin': fields.Integer(required=True, description='0:False,1:True', example=0, min=0, max=1),
   'Browser': fields.String(required=False, description='Browser used by account holder'),
   'Notification': fields.String(required=False, description='I don\'t know what this is'),
}


