
from google.appengine.ext import ndb
import datetime

class Doctor(ndb.Model):
      username = ndb.StringProperty(default="Choose a Username")
      bio = ndb.TextProperty(default="Enter your bio here")
      notifyEmail = ndb.StringProperty(default="me@email.com")
      followers = ndb.KeyProperty(repeated=True)
      following = ndb.KeyProperty(repeated=True)
      liked = ndb.KeyProperty(repeated=True)
      designation= ndb.TextProperty(default="doctor")
      organization=ndb.TextProperty()
      field=ndb.TextProperty(default="general")
      specialization=ndb.TextProperty(default="none")
      idNumber=ndb.IntergerProperty()
      province=ndb.TextProperty()
      ethnicGroup=ndb.TextProperty()
      city=ndb.TextProperty()
      address=ndb.KeyProperty(repeated=True)
      gender=ndb.TextProperty()
      dateOfBirth=ndb.DateTimeProperty()
      contactNumber=ndb.TextProperty()
      mobileNumber=ndb.TextProperty()
      created = ndb.DateTimeProperty(default=datetime.datetime.now()
      verified = ndb.BooleanProperty(default=False)
    
class Address(ndb.Model):
      street = ndb.StringProperty()
      address = ndb.StringProperty()
      province=ndb.StringProperty()
      code=ndb.StringProperty()
      city=ndb.StringProperty()
      country=ndb.StringProperty()

