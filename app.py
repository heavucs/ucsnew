#!/usr/bin/python

## These two lines are needed to run on EL6
__requires__ = ['jinja2 >= 2.4']
import pkg_resources

from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
#from flask.ext.sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://ucs:ucsonline@localhost/ucs_2016'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Item(db.Model):
   __tablename__ = 'Item'
   ID = db.Column(db.Integer, primary_key=True)
   ItemNumber = db.Column(db.Unicode(15), unique=True)
   MemberNumber =  db.Column(db.Unicode(15))
   Description = db.Column(db.Unicode(50))
   Category = db.Column(db.Unicode(25))
   Subject = db.Column(db.Unicode(25))
   Publisher = db.Column(db.Unicode(50))
   Year = db.Column(db.Unicode(4))
   ISBN = db.Column(db.Unicode(50))
   Condition = db.Column(db.Integer())
   ConditionDetail = db.Column(db.Unicode(128))
   NumItems = db.Column(db.Integer())
   FridayPrice = db.Column(db.Numeric())
   SaturdayPrice = db.Column(db.Numeric())
   Donate = db.Column(db.Boolean)
   CheckedIn = db.Column(db.Date)
   CheckedOut = db.Column(db.Date)
   Status = db.Column(db.Integer())
   Deleted = db.Column(db.Boolean)
   Printed = db.Column(db.Boolean)

   def __init__(self, ItemNumber, MemberNumber, Description, Category, Subject, Publisher, Year, ISBN, Condition, ConditionDetail, NumItems, FridayPrice, SaturdayPrice, Donate, CheckedIn, CheckedOut, Status, Deleted, Printed):
      self.ItemNumber = ItemNumber
      self.MemberNumber = MemberNumber
      self.Description = Description
      self.Category = Category
      self.Subject = Subject
      self.Publisher = Publisher
      self.Year = Year
      self.ISBN = ISBN
      self.Condition = Condition
      self.ConditionDetail = ConditionDetail
      self.NumItems = NumItems
      self.FridayPrice = FridayPrice
      self.SaturdayPrice = SaturdayPrice
      self.Donate = Donate
      self.CheckedIn = CheckedIn
      self.CheckedOut = CheckedOut
      self.Status = Status
      self.Deleted = Deleted
      self.Printed = Printed

   def __repr__(self):
      return '<Item %r>' % self.ItemNumber

class Account(db.Model):
   __tablename__ = 'Account'
   ID = db.Column(db.Integer, primary_key=True)
   MemberNumber = db.Column(db.Unicode(15), unique=True)
   Established = db.Column(db.Date)
   FirstName = db.Column(db.Unicode(25))
   LastName = db.Column(db.Unicode(25))
   Address = db.Column(db.Unicode(128))
   Address2 = db.Column(db.Unicode(128))
   City = db.Column(db.Unicode(128))
   State = db.Column(db.Unicode(2))
   Zip = db.Column(db.Unicode(5))
   Phone = db.Column(db.Unicode(10))
   Email = db.Column(db.Unicode(128))
   Password = db.Column(db.Unicode(32))
   Question = db.Column(db.Unicode(50))
   Answer = db.Column(db.Unicode(50))
   ActivationCode = db.Column(db.Unicode(128))
   Activated = db.Column(db.Date)
   Admin = db.Column(db.Boolean)
   Browser = db.Column(db.Unicode(128))
   Notification = db.Column(db.Integer)

   def __init__(MemberNumber, Established, FirstName, LastName, Address, Address2, City, State, Zip, Phone, Email, Password, Question, Answer, ActivationCode, Activated, Admin, Browser, Notification):
      self.MemberNumber = MemberNumber
      self.Established = Established
      self.FirstName = FirstName
      self.LastName = LastName
      self.Address = Address
      self.Address2 = Address2
      self.City = City
      self.State = State
      self.Zip = Zip
      self.Phone = Phone
      self.Email = Email
      self.Password = Password
      self.Question = Question
      self.Answer = Answer
      self.ActivationCode = ActivationCode
      self.Activated = Activated
      self.Admin = Admin
      self.Browser = Browser
      self.Notification = Notification

   def __repr__(self):
      return '<Account %r>' % self.ID

#@app.route('/')
#def index():
#   return '<!DOCTYPE html><html><body>Hello World<br><a href="/cakes">cakes</a></body></html>'

@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
   return render_template('hello.html', name=name)

@app.route('/')
def index():
   return render_template('index.html')

@app.route('/checkout/account', methods=['GET'])
def account(pageid="account"):
   if request.args.get('ID'):
      lookupAcnt = request.args.get('ID')
   else:
      lookupAcnt = 1
   if request.args.get('page'):
      page = request.args.get('page')
   else:
      page = 1
   lookupaccount = Account.query.filter_by(ID=lookupAcnt).all()
   return render_template('account.html', pageid=pageid, lookupaccount=lookupaccount, lookupAcnt=lookupAcnt)

@app.route('/checkout/item/lookup', methods=['GET','POST'])
def itemlookup(pageid="item"):
   #lookupID = request.args.get('ItemNumber', type=str, default=1)
   #page = request.args.get('page', type=int, default=1)
   if request.is_json:
      request_data = request.get_json()
      if 'lookupID' in request_data:
         lookupID = request_data['lookupID']
      else:
         lookupID = 1
      if 'page' in request_data:
         page = request_data['page']
      else:
         page = 1
   else:
      lookupID = 1
      page = 1
   pagination = Item.query.filter(Item.ID.like("%s%s"%(lookupID,"%"))).paginate(page=page, per_page=25, error_out=False)
   response = jsonify(pageid=pageid)
   return response

@app.route('/checkout/item', methods=['GET','POST'])
def item(pageid="item"):
   if request.is_json:
      request_data = request.get_json()
      if 'lookupID' in request_data:
         lookupID = request_data['lookupID']
      else:
         lookupID = 1
      if 'page' in request_data:
         page = request_data['page']
      else:
         page = 1
   else:
      lookupID = request.args.get('ItemNumber', type=str, default=1)
      page = request.args.get('page', type=int, default=1)
      #lookupID = 1
      #page = 1
   pagination = Item.query.filter(Item.ID.like("%s%s"%(lookupID,"%"))).paginate(page=page, per_page=25, error_out=False)
   return render_template('item.html', pageid=pageid, page=page, lookupID=lookupID, pagination=pagination)

@app.route('/checkout')
@app.route('/checkout/')
@app.route('/checkout/<pageid>')
def checkout(pageid=None):
   return render_template('index.html', pageid=pageid)

if __name__ == '__main__':
   app.run(debug=True, host='0.0.0.0')

