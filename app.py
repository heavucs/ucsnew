#!/usr/bin/python

## These two lines are needed to run on EL6
__requires__ = ['jinja2 >= 2.4']
import pkg_resources

from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
#from flask.ext.sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://ucs:ucsonline@localhost/ucs_2016'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Item(db.Model):
   __tablename__ = 'Item'
   ID = db.Column(db.Integer(), primary_key=True)
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
      self.ItemNumber = itemnumber
      self.MemberNumber = membernumber
      self.Description = description
      self.Category = category
      self.Subject = subject
      self.Publisher = publisher
      self.Year = year
      self.ISBN = isbn
      self.Condition = condition
      self.ConditionDetail = conditiondetail
      self.NumItems = numitems
      self.FridayPrice = fridayprice
      self.SaturdayPrice = saturdayprice
      self.Donate = donate
      self.CheckedIn = checkedin
      self.CheckedOut = checkedout
      self.Status = status
      self.Deleted = deleted
      self.Printed = printed

   def __repr__(self):
      return '<Item %r>' % self.ItemNumber

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

@app.route('/checkout/item', methods=['GET'])
def item(pageid="item"):
   if request.args.get('ItemNumber'):
      lookupID = request.args.get('ItemNumber')
   else:
      lookupID = 1
   if request.args.get('page'):
      page = request.args.get('page')
   else:
      page = 1
   lookupitem = Item.query.filter_by(ID=lookupID).all()
   #lookupitem = Item.query.paginate(page=page, per_page=25)
   lookupquery = lookupID
   return render_template('item.html', pageid=pageid, lookupitem=lookupitem, lookupquery=lookupquery, lookupID=lookupID)

@app.route('/checkout')
@app.route('/checkout/')
@app.route('/checkout/<pageid>')
def checkout(pageid=None):
   return render_template('index.html', pageid=pageid)

if __name__ == '__main__':
   app.run(debug=True, host='0.0.0.0')

