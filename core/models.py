from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Item(db.Model):
   __tablename__ = 'Item'
   ID = db.Column(db.Integer, primary_key=True)
   ItemNumber = db.Column(db.Unicode(15), unique=True)
   #MemberNumber = db.relationship('Account', backref='MemberNumber', lazy='dynamic')
   MemberNumber = db.Column(db.Unicode(15), db.ForeignKey('Account.MemberNumber'))
   #Account_ID = db.Column(db.Unicode(15), db.ForeignKey('Account.ID'))
   #MemberNumber = db.Column(db.Unicode(15))
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
   MemberNumber = db.Column(db.Unicode(15))
   #MemberNumber = db.Column(db.Unicode(15), db.ForeignKey('Item.MemberNumber'))
   #Items = db.relationship('Item', backref='MemberNumber', lazy='dynamic')
   Items = db.relationship('Item')
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

