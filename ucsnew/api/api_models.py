from flask_restplus import fields

RE_PHONENUMBER = r'^[0-9]{10}$'
RE_ZIP = r'^[0-9]{5}$'

item_model = {
        'itemnumber': fields.String(
            readonly=True,
            required=False,
            description='ItemNumber within Account'
            ),
        'membernumber': fields.String(
            required=True,
            description='Account Number'
            ),
        'description': fields.String(
            required=True,
            description='Description of the item'
            ),
        'category': fields.String(
            required=True,
            description='Item\'s Category'
            ),
        'subject': fields.String(
            required=True,
            description='School subject'
            ),
        'publisher': fields.String(
            required=False,
            description='Book Publisher'
            ),
        'year': fields.String(
            required=False,
            description='Published Year'
            ),
        'isbn': fields.String(
            required=False,
            description='Book\'s ISBN number'
            ),
        'condition': fields.Integer(
            required=False,
            description='0:Poor,1:BelowAverage,2:Average,3:Good,4:New',
            example=4,
            min=0,
            max=4
            ),
        'conditiondetail': fields.String(
            required=False,
            description='Additional comments on condition'
            ),
        'numitems': fields.Integer(
            required=True,
            description='Number of items included in "Item" e.g. a set of books',
            example=1,
            min=1
            ),
        'price': fields.String(
            required=True,
            description='Friday price',
            example="1.00"
            ),
        'discountprice': fields.String(
            required=True,
            description='Saturday price',
            example="1.00"
            ),
        'donate': fields.Integer(
            required=True,
            description='0:False,1:True',
            min=0,
            max=1,
            example=0
            ),
        'checkedin': fields.String(
            required=False,
            description='The presense of a datetime indicates checkedin'
            ),
        'checkedout': fields.String(
            required=False,
            description='The presense of a datetime indicates sold'
            ),
        'status': fields.Integer(
            required=True,
            description='0:Pending,1:CheckedIn,2:Sold,3:PickedUp,4:Deleted',
            example=0,
            min=0,
            max=4
            ),
        'deleted': fields.Integer(
            required=False,
            description='0:False,1:True',
            min=0,
            max=1,
            example=0
            ),
        #'printed': fields.Integer(
        #    required=False,
        #    description='0:False,1:True',
        #    min=0,
        #    max=1,
        #    example=0
        #    ),
        }

delete_item_model = {}

member_model = {
        'membernumber': fields.String(
            required=True,
            description='Account Number'
            ),
        'established': fields.DateTime(
            required=True,
            description='DateTime account was created'
            ),
        'firstname': fields.String(
            required=True,
            description='First name associated with Account'
            ),
        'lastname': fields.String(
            required=True,
            description='Last name associated with Account'
            ),
        'address': fields.String(
            required=True,
            description='Mailing address 1'
            ),
        'address2': fields.String(
            required=True,
            description='Mailing address 2'
            ),
        'city': fields.String(
            required=True,
            description='Mailing city'
            ),
        'state': fields.String(
            required=True,
            description='Mailing state'
            ),
        'zipcode': fields.String(
            required=True,
            description='Mailing zip',
            example='12345',
            pattern=RE_ZIP
            ),
        'phone': fields.String(
            required=True,
            description='Contact number',
            example='1231231234',
            pattern=RE_PHONENUMBER
            ),
        'email': fields.String(
            required=True,
            descrpition='Contact e-mail'
            ),
        'password': fields.String(
            required=True,
            description='Account password'
            ),
        'question': fields.String(
            required=True,
            description='Secret question for password retrieval'
            ),
        'answer': fields.String(
            required=True,
            description='Secret answer for secret question'
            ),
        'activationcode': fields.String(
            required=True,
            description='Activation code'
            ),
        'activated': fields.DateTime(
            required=True,
            description='DateTime Account was activated'
            ),
        'admin': fields.Integer(
            required=True,
            description='0:False,1:True',
            example=0,
            min=0,
            max=1
            ),
        'browser': fields.String(
            required=False,
            description='Browser used by account holder'
            ),
        'notification': fields.String(
            required=False,
            description='I don\'t know what this is'
            ),
        }

delete_member_model = {}

user_model = {
        'username': fields.String(required=False, description='username'),
        'password': fields.String(required=False, description='password'),
        'firstname': fields.String(required=False, description='First name'),
        'lastname': fields.String(required=False, description='Last name'),
        }

delete_user_model = {}
