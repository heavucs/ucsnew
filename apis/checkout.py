from flask_restplus import Namespace, Resource, fields

api = Namespace('Checkout', Description='Checkout related functions')

@api.route('/')
def index():
   return render_template('index.html')

@api.route('/checkout/account', methods=['GET','POST'])
def account(pageid="account"):
   if request.method == 'POST':
      if request.form['ID']:
         ID = request.form['ID']
      else:
         ID = ""
      if request.form['MemberNumber']:
         MemberNumber = request.form['MemberNumber']
      else:
         MemberNumber = ""
      if request.form['LastName']:
         LastName = request.form['LastName']
      else:
         LastName = ""
      if request.form['PhoneNumber']:
         PhoneNumber = request.form['PhoneNumber']
      else:
         PhoneNumber = ""
      if request.form['Page']:
         if not request.form['Page'] == 'NaN':
            page = int(request.form['Page'])
         else:
            page = 1
      else:
         page = 1
      pagination = (Account.query
         .join(Item, Account.MemberNumber == Item.MemberNumber)
         .with_entities(Account.ID,Account.MemberNumber,Account.FirstName,Account.LastName,db.func.count(Item.ID).label("Items"),Account.Activated)
         .filter(Account.ID.like("%s%s"%(ID,"%")))
         .filter(Account.MemberNumber.like("%s%s"%(MemberNumber,"%")))
         .filter(Account.LastName.like("%s%s"%(LastName,"%")))
         .filter(Account.Phone.like("%s%s"%(PhoneNumber,"%")))
         .group_by(Account.MemberNumber)
         .paginate(page=page, per_page=25, error_out=False))
      return render_template('accountresults.html', pageid=pageid, page=page, pagination=pagination)
   else:
      return render_template('account.html', pageid=pageid)

@api.route('/checkout/item', methods=['GET','POST'])
def item(pageid="item"):
   if request.method == 'POST':
      if request.form['ItemNumber']:
         ItemNumber = request.form['ItemNumber']
      else:
         ItemNumber = ""
      if request.form['AccountNumber']:
         AccountNumber = request.form['AccountNumber']
      else:
         AccountNumber = ""
      if request.form['Description']:
         Description = request.form['Description']
      else:
         Description = ""
      if request.form['Page']:
         if not request.form['Page'] == 'NaN':
            page = int(request.form['Page'])
         else:
            page = 1
      else:
         page = 1
      pagination = (Item.query
         .filter(Item.ID.like("%s%s"%(ItemNumber,"%")))
         .filter(Item.MemberNumber.like("%s%s"%(AccountNumber,"%")))
         .filter(Item.Description.like("%s%s%s"%("%",Description,"%")))
         .paginate(page=page, per_page=25, error_out=False))
      return render_template('itemresults.html', pageid=pageid, page=page, pagination=pagination)
   else:
      return render_template('item.html', pageid=pageid)

@api.route('/checkout')
@api.route('/checkout/')
@api.route('/checkout/<pageid>')
def checkout(pageid=None):
   return render_template('index.html', pageid=pageid)



