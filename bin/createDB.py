#!/usr/bin/python
import sys
import MySQLdb

#db = MySQLdb.connect(host="localhost",user="ucs",passwd="ucsonline",db="ucs_2015")
#cur = db.cursor()
#arg1 = 'jdixon'
#sql = "select * from Checkers where loginid = '{0}'".format(arg1)
#cur.execute(sql)

def question():
   question = 'Are you sure you want to continue?  Continuing WILL DESTROY any previous database. (Type "YES" to continue)\n'
   sys.stdout.write(question)
   choice = raw_input()
   if choice == "YES":
      sys.stdout.write("Creating Database\n")
   else:
      sys.stdout.write("NO\n")
      sys.exit()

question()


db = MySQLdb.connect(host="localhost",user="ucsnew",passwd="heav ucs 2013")
cur = db.cursor()
#sql = ''
#cur.execute(sql)
sql = """
   DROP DATABASE ucsnew;
   CREATE DATABASE ucsnew;
"""
cur.execute(sql)
cur.close()
db.close()
sys.stdout.write("Database Created\n")

sys.stdout.write("Creating Tables\n")
db = MySQLdb.connect(host="localhost",user="ucsnew",passwd="heav ucs 2013",db="ucsnew")
cur = db.cursor()
sql = """
  CREATE TABLE checker (
  checker_id INT(11) NOT NULL,
  checker_username VARCHAR(16) NOT NULL,
  checker_firstname VARCHAR(32) NOT NULL,
  checker_lastname VARCHAR(32) NOT NULL,
  checker_admin BOOL NULL DEFAULT 0,
  PRIMARY KEY(checker_id)
)
TYPE=InnoDB;

CREATE TABLE account (
  account_id INT(11) NOT NULL AUTO_INCREMENT,
  account_membernumber VARCHAR(15) NULL,
  account_established DATE NULL,
  account_firstname VARCHAR(25) NULL,
  account_lastname VARCHAR(25) NULL,
  account_address VARCHAR(128) NULL,
  account_address2 VARCHAR(128) NULL,
  account_city VARCHAR(64) NULL,
  account_state VARCHAR(2) NULL,
  account_zip VARCHAR(5) NULL,
  account_phone VARCHAR(10) NULL,
  account_email VARCHAR(128) NULL,
  account_password VARCHAR(32) NULL,
  account_question VARCHAR(50) NULL,
  account_answer VARCHAR(50) NULL,
  account_activationcode VARCHAR(128) NULL,
  account_activated DATE NULL,
  account_admin BOOL NULL,
  account_browser TEXT NULL,
  account_notification INT(11) NULL,
  PRIMARY KEY(account_id)
)
TYPE=InnoDB;

CREATE TABLE transaction (
  transaction_id INT(11) NOT NULL AUTO_INCREMENT,
  checker_id INT(11) NOT NULL,
  transaction_date TIMESTAMP NOT NULL DEFAULT '0000-00-00 00:00:00',
  transaction_state INT(1) NOT NULL DEFAULT 0,
  transaction_paymenttype INT(1) NULL,
  transaction_paymentnote VARCHAR(99) NULL,
  transaction_paymentamount DECIMAL NULL,
  transaction_paymenttotal DECIMAL NULL,
  PRIMARY KEY(transaction_id),
  INDEX transaction_FKIndex1(checker_id),
  FOREIGN KEY(checker_id)
    REFERENCES checker(checker_id)
      ON DELETE NO ACTION
      ON UPDATE NO ACTION
)
TYPE=InnoDB;

CREATE TABLE item (
  item_id INT(11) NOT NULL AUTO_INCREMENT,
  account_id INT(11) NOT NULL,
  item_itemnumber INT(11) NOT NULL,
  item_membernumber VARCHAR(15) NOT NULL,
  item_description VARCHAR(50) NOT NULL,
  item_category VARCHAR(25) NOT NULL,
  item_subject VARCHAR(25) NOT NULL,
  item_publisher VARCHAR(50) NOT NULL,
  item_year INT(4) NOT NULL,
  item_isbn VARCHAR(50) NOT NULL,
  item_condition INT(11) NOT NULL DEFAULT 0,
  item_numitems INT(11) NOT NULL DEFAULT 0,
  item_fridayprice DECIMAL NOT NULL DEFAULT 0,
  item_saturdayprice DECIMAL NOT NULL DEFAULT 0,
  item_donate BOOL NOT NULL DEFAULT 0,
  item_checkedin TIMESTAMP NOT NULL DEFAULT '0000-00-00 00:00:00',
  item_checkedout TIMESTAMP NOT NULL DEFAULT '0000-00-00 00:00:00',
  item_status INT(11) NULL DEFAULT 0,
  item_deleted BOOL NOT NULL DEFAULT 0,
  item_printed BOOL NOT NULL DEFAULT 0,
  PRIMARY KEY(item_id),
  INDEX item_FKIndex1(account_id),
  FOREIGN KEY(account_id)
    REFERENCES account(account_id)
      ON DELETE NO ACTION
      ON UPDATE NO ACTION
)
TYPE=InnoDB;

CREATE TABLE transaction_item (
  transaction_id INT(11) NOT NULL,
  item_id INT(11) NOT NULL,
  transaction_item_sellprice DECIMAL NOT NULL,
  INDEX transaction_item_FKIndex1(item_id),
  INDEX transaction_item_FKIndex2(transaction_id),
  FOREIGN KEY(item_id)
    REFERENCES item(item_id)
      ON DELETE NO ACTION
      ON UPDATE NO ACTION,
  FOREIGN KEY(transaction_id)
    REFERENCES transaction(transaction_id)
      ON DELETE NO ACTION
      ON UPDATE NO ACTION
)
TYPE=InnoDB;
"""
cur.execute(sql)
cur.close()
db.close()
sys.stdout.write("Tables Created\n")

