#!/usr/bin/env python
import os
import sys
import uuid
import datetime

import argparse

import MySQLdb as sql

from flask import current_app

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError


if __name__ == '__main__':
    approot = "{}/approot".format(os.environ['VIRTUAL_ENV'])
    sys.path.append(approot)

    # Parse arguments and load config file
    parser = argparse.ArgumentParser(description='Load data from legacy database.')
    parser.add_argument('-c', '--config', required=True, metavar='"configfile"',
            help='Name of local config file')
    
    args = parser.parse_args()
    configfile = "{}/{}".format(approot, args.config)
    
    # Load application
    try:
        from ucsnew import create_app
    except ImportError as e:
        print(e)
        sys.exit(1)
    except:
        print("Unable to load module: ucsnew")
        sys.exit(1)

    app = create_app(configfile=configfile)

    #import logging
    #logging.basicConfig()
    #logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

    from ucsnew.models import db
    from ucsnew.models import Member
    from ucsnew.models import Item

    with app.app_context():
        print(db)
        print(db.session)


    # Import legacy data

    with app.app_context():

        legacy_db = sql.connect(
                host=app.config['LEGACY_UCS_SQLHOST'],
                user=app.config['LEGACY_UCS_SQLUSER'],
                passwd=app.config['LEGACY_UCS_SQLPASS'],
                db=app.config['LEGACY_UCS_SQLDB']
                )
        legacy_db.c = legacy_db.cursor()
        nullstring = lambda x: x if x else ''

        # Import Member Accounts from legacy database
        legacy_db.c.execute("""SELECT MemberNumber, Established, FirstName,
                LastName, Address, Address2, City, State, Zip, Phone, Email,
                Password, Question, Answer, ActivationCode, Activated, Admin,
                Browser, Notification FROM Account""")
        legacy_members_l = legacy_db.c.fetchall()

        print("FIXME: legacy_members_l: %s" % len(legacy_members_l))

        for i in legacy_members_l:

            if not i[0]:
                continue

            new_member_d = {
                    'membernumber': i[0],
                    'established': i[1],
                    'firstname': i[2],
                    'lastname': i[3],
                    'address': i[4],
                    'address2': i[5],
                    'city': i[6],
                    'state': i[7],
                    'zipcode': i[8],
                    'phone': i[9],
                    'email': i[10],
                    'password': i[11],
                    'question': i[12],
                    'answer': i[13],
                    'activationcode': i[14],
                    'activated': i[15],
                    'admin': i[16].decode('utf-8'),
                    'browser': i[17],
                    'notification': i[18],
                    }


            db_member = Member(
                    new_member_d['membernumber'],
                    new_member_d['established'],
                    new_member_d['firstname'],
                    new_member_d['lastname'],
                    new_member_d['address'],
                    new_member_d['address2'],
                    new_member_d['city'],
                    new_member_d['state'],
                    new_member_d['zipcode'],
                    new_member_d['phone'],
                    new_member_d['email'],
                    new_member_d['password'],
                    new_member_d['question'],
                    new_member_d['answer'],
                    new_member_d['activationcode'],
                    new_member_d['admin'],
                    )

            db.session.add(db_member)
            db_member_d = db_member.as_api_dict()
            print(new_member_d)

        # Import Items from legacy database
        legacy_db.c.execute("""SELECT ID, ItemNumber, Description, Category,
                Subject, Publisher, Year, ISBN, `Condition`, ConditionDetail,
                NumItems, FridayPrice, SaturdayPrice, Donate, CheckedIn,
                CheckedOut, Status, Deleted, MemberNumber
                FROM Item""")
        legacy_items_l = legacy_db.c.fetchall()

        for i in legacy_items_l:

            # If membernumber is null
            if not i[18]:
                continue

            new_item_d = {
                    'uuid': uuid.uuid4(),
                    'itemnumber': i[1],
                    'membernumber': i[18],
                    'description': i[2],
                    'category': i[3],
                    'subject': i[4],
                    'publisher': i[5],
                    'year': i[6],
                    'isbn': i[7],
                    'condition': i[8],
                    'conditiondetail': i[9],
                    'numitems': i[10],
                    'price': i[11],
                    'discountprice': i[12],
                    'donate': i[13].decode('utf-8'),
                    }

            db_item = Item(
                    new_item_d['uuid'],
                    new_item_d['itemnumber'],
                    new_item_d['membernumber'],
                    new_item_d['description'],
                    new_item_d['category'],
                    new_item_d['subject'],
                    new_item_d['publisher'],
                    new_item_d['year'],
                    new_item_d['isbn'],
                    new_item_d['condition'],
                    new_item_d['conditiondetail'],
                    new_item_d['numitems'],
                    new_item_d['price'],
                    new_item_d['discountprice'],
                    new_item_d['donate'],
                    )

            db.session.add(db_item)
            new_item_d = db_item.as_api_dict()
            print(new_item_d)

        try:
            db.session.commit()
        except IntegrityError as e:
            print("IntegrityError: {}".format(e))
            print("ERROR: Unable to create resource: IntegrityError")

        sys.exit(0)
