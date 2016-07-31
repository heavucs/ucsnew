#!/usr/bin/python

## These two lines are needed to run on EL6
__requires__ = ['jinja2 >= 2.4']
import pkg_resources

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
#from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://ucs:ucsonline@localhost/ucs_2016'
db = SQLAlchemy(app)

class Item(db.Model):
   ID = db.Column(db.Integer(11), primary_key=True)
   ItemNumber = db.Column(db.String(15), unique=True)
   MemberNumber =  db.Column(db.String(15))
   Description = db.Column(db.String(50))
   Category = db.Column(db.String(25))
   Subject = db.Column(db.String(25))
   Publisher = db.Column(db.String(50))
   Year = db.Column(db.String(4))
   ISBN = db.Column(db.String(50))
   Condition = db.Column(db.Integer(11))
   ConditionDetail = db.Column(db.String(128))
   NumItems = db.Column(db.Integer(11))
   FridayPrice = db.Column(db.float)
   SaturdayPrice = db.Column(db.float)
   Donate = db.Column(db.boolean)
   CheckedIn = db.Column(db.date)
   CheckedOut = db.Column(db.date)
   Status = db.Column(db.Integer(11))
   Deleted = db.Column(db.boolean)
   Printed = db.Column(db.boolean)

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

@app.route('/checkout')
@app.route('/checkout/')
@app.route('/checkout/<pageid>')
def checkout(pageid=None):
   return render_template('index.html', pageid=pageid)

if __name__ == '__main__':
   app.run(debug=True, host='0.0.0.0')

