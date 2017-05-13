#!/usr/bin/python

from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
#from flask_restplus import Api, Resource, fields
from flask_restplus import Api, Resource
from apis import api
from core.models import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://ucs:ucsonline@localhost/ucs_2016'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
api.init_app(app)

if __name__ == '__main__':
   app.run(debug=True, host='0.0.0.0')

