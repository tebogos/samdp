import webapp2
import jinja2
import os
import logging
from models import models
import datetime
import time
import base64
import json
from pyjwt import jwt  # Requires: pip install python-jwt
import Crypto.PublicKey.RSA as RSA  # Requires: pip install pycrypto

from google.appengine.ext import ndb
from google.appengine.api import users , memcache , app_identity
from apiclient.discovery import build
from oauth2client.contrib.appengine import OAuth2Decorator

profileauthdecorator = OAuth2Decorator(
            client_id='705607693138-7e0nkaictkp5u64vj71ngih6085pmr6e.apps.googleusercontent.com',
            client_secret='5_Z9T-7JruwFiDSaflfYo-I2',
            scope='https://www.googleapis.com/auth/plus.login')

file=open('public/svg/twitter.svg','r')
try:
   twitter_svg=file.read()
finally:
   file.close()

file=open('public/svg/google.svg','r')
try:
  google_svg=file.read()
finally:
  file.close()

file=open('public/svg/facebook.svg','r')
try:
  facebook_svg=file.read()
finally:
  file.close()

_FIREBASE_CONFIG = '_firebase_config.html'

_IDENTITY_ENDPOINT = ('https://identitytoolkit.googleapis.com/'
                      'google.identity.identitytoolkit.v1.IdentityToolkit')
_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

def create_custom_token(uid, valid_minutes=60):
    """Create a secure token for the given id.
    This method is used to create secure custom JWT tokens to be passed to
    clients. It takes a unique id (uid) that will be used by Firebase's
    security rules to prevent unauthorized access. In this case, the uid will
    be the channel id which is a combination of user_id and game_key
    """

    # use the app_identity service from google.appengine.api to get the
    # project's service account email automatically
    service_account_email = "firebase@samdp-website.iam.gserviceaccount.com"
    private_key = RSA.importKey("-----BEGIN PRIVATE KEY-----\nMIIEwAIBADANBgkqhkiG9w0BAQEFAASCBKowggSmAgEAAoIBAQC/vCoaEB6Pj+m0\nGO74XTzgDuvQkcmemn8HPhz0wAKc4xA1+f0dj3DJEQ93NeeZd+vbrZA/01AZMNlw\n7Suae3y0wzJwtLBhEncNjfwaI51GoPyhb8cq2CsN2a7Z1Xxyl0GphRvrk4woS7v7\n3OFscQvAFjuJU5x6enWXDMluQIAMI5uE0bJZJxISq8W0+7B0VXSmh4I/KqMmjqFK\n08OfhKMiqWHF/Fv5ulTkefd5P/MZjKWxTxBTABpfCB4g2pXxlnyXvwUI3/H/7W7s\nS50mc+bfixcL7T4yNYQgTG09DN5qq6VQMHwImiyOK/QrBcEVAfIV95KFJ/SJSbp9\nPqau1J11AgMBAAECggEBAL1+d1HI6ptSTVRsbAnVBGwg8xjwbQauhKsgzTdraWmq\n1AO0rV+Au6RMky9rfBjmN5mmgPFDpF8xM0XzcOu97fMtE/Xl7ogR2s3vrOAcoL0E\nMIpQ0dPbTzniEXhDETqjmQa0gnKiIZxVtVVn6PbnBwjyMCc6FmXKD9uYjJ/FaYgU\nFqayBSgwu61FnYzwWp8buQPhOzd6AQ09XYB6PVhOnVFLIY+JRHKj4I3jIYYBN2k6\nFf1fgqu5//ei1muhZMnqlu2bg/wv9TxgNWO7fkdRNTkMNGTB2Qx/LFONGutJwCHZ\ngVpHOpXg4gc6HtaANdrQtLRtKMipuwJb9kUddJrpikUCgYEA5+ik/cPpJ0jnHqSA\nrsInuJnAx0z/IQG4PP6r0sgUGOeO75KDND6JCvqoqnZKNZGBJX7UDvM/y8gWQFUX\nbowjUZqUzpuMMet73f/US9HquCyzQHEutpLjB/5jniKO2i/G4Qle41gw+3cgcaiW\n9O4YpbIWPc6364AqF9onmEcBD2sCgYEA06ck0CVlzh4WVFCl2iuaPSsD2Hq3U23/\nmbLkM5hfHYli7fKYdEcG09Ux/YlUiWTMrkGo3V7tK/bWnlCYR9wmgAoffcvlZ+qn\nPY1jUItgk9HD0FMD8T2YOba1BuTQ8qG0W2msKvp0/nOc+ydUgj0CxwIqeA895IXs\nmoK6oHr4np8CgYEAuxMlvXvDYihiIIrtL4x5xGVraJqJGJQtji6WZvN1mt14pXPY\nGVX08QFg/BluJaZZuuiDogfBx96BbKX3v/qWJyb+sWgzALYIdv3/wKX2pVmRxANJ\nfoghUnp428De4c02rqQDgnvLD596cZVhKPXEti1h2bwfC3+Y9SLLXACzLz8CgYEA\nswtiCPKZ/JNXMFxI8RaRk80fo7GsA9e5sbuzcDIlxEbEeaYPcc3j6K8haukRqmiq\n/X5t61ayK87UH3juWVvS9d2aZkBmAFJwx5Ejwq8lM+bvTvvrCdihPbFh0kMevyIs\nAGiUTIczEU2cLppG0yXpg5BBfO7n3LmuPcb5OWjNiOECgYEAw/+P5PYwp7q0KAjr\nED66PVsCuH6iTa59gtXSR5Yrb9cUS1ownaCDPEV36n3JxQWfMw7c5T1xNtKLHT4Y\n2kGxsZkHr94Wj32tO+BI6AQvTgw70O70P2qlc6RYe8XCcewsPKZQovrHMh5JYhpc\nOB6kgeV8ggsD7ZrCnILfe6EakQM=\n-----END PRIVATE KEY-----\n")

    try:
        payload = {
            "iss": service_account_email,
            "sub": service_account_email,
            "aud": _IDENTITY_ENDPOINT,
            "uid": uid,
            "claims": {
                "displayName": "Tebza Ngwana"
              }
        }
        exp = datetime.timedelta(minutes=60)
        return jwt.generate_jwt(payload, private_key, "RS256", exp)
    except Exception as e:
        print "Error creating custom token: " + e.message
        return None


class _BaseHandler(webapp2.RequestHandler):
    def initialize(self, request, response):
        super(_BaseHandler, self).initialize(request, response)

        self.user = users.get_current_user()
        
             
        if self.user:
            logging.info("User ID : "+self.user.user_id()) 
            imgUrl=self.getUserImg()
            self.template_values = {
                'user': self.user,
                'is_admin': users.is_current_user_admin(),
                'logout_url': users.create_logout_url('/'),
                'imgUrl':imgUrl
                }
            memcache.set('isAuth', True)
            memcache.set('user',self.user)
            logging.error('Print user')
            logging.error(memcache.get('user'))
        else:
            self.template_values = {
                'login_url': users.create_login_url(self.request.url)}
    @profileauthdecorator.oauth_required
    def getUserImg(self):
       
        auth_http = profileauthdecorator.http()
        logging.info(auth_http)
        service = build('plus', 'v1', http=auth_http)
        people_resource = service.people()
        people_document = people_resource.get(userId='me').execute()
        imgUrl= people_document['image']['url']
        return imgUrl


class MainPage(_BaseHandler):
    
    def get(self):
        logging.info('MainPage class requested')
        user=users.get_current_user()
        if  user:
            logging.info("User ID"+user.user_id())
       

        self.template_values['svg']={
        'facebook': facebook_svg,
        'google': google_svg,
        'twitter': twitter_svg
          }

        
        template = jinja_environment.get_template('views/home.template')
        self.response.out.write(template.render(self.template_values))

class ContactsPage(_BaseHandler):
    def get(self):
        logging.info('ContactsPage class requested')

        self.template_values['svg']={
        'facebook': facebook_svg,
        'google': google_svg,
        'twitter': twitter_svg
          }

        template = jinja_environment.get_template('views/contacts.template')
        self.response.out.write(template.render(self.template_values))


class NewsPage(_BaseHandler):
    def get(self):
        logging.info('DocumentsPage class requested')

        self.template_values['svg']={
        'facebook': facebook_svg,
        'google': google_svg,
        'twitter': twitter_svg
          }

        template = jinja_environment.get_template('views/documents.template')
        self.response.out.write(template.render(self.template_values))

class TermsOfUsePage(_BaseHandler):
    def get(self):
        logging.info('TermsOfUse class requested')

        self.template_values['svg']={
        'facebook': facebook_svg,
        'google': google_svg,
        'twitter': twitter_svg
          }

        template = jinja_environment.get_template('views/terms-of-use.template')
        self.response.out.write(template.render(self.template_values))

class PrivacyPolicyPage(_BaseHandler):
    def get(self):
        logging.info('PrivacyPolicyPage class requested')

        self.template_values['svg']={
        'facebook': facebook_svg,
        'google': google_svg,
        'twitter': twitter_svg
          }

        template = jinja_environment.get_template('views/privacy-policy.template')
        self.response.out.write(template.render(self.template_values))

class PeePage(_BaseHandler):
    def get(self):
        logging.info('PeePage class requested')

        self.template_values['svg']={
        'facebook': facebook_svg,
        'google': google_svg,
        'twitter': twitter_svg
          }

        template = jinja_environment.get_template('views/pee.template')
        self.response.out.write(template.render(self.template_values))

class ConsultingPage(_BaseHandler):
    def get(self):
        logging.info('ConsultingPage class requested')

        self.template_values['svg']={
        'facebook': facebook_svg,
        'google': google_svg,
        'twitter': twitter_svg
          }

        template = jinja_environment.get_template('views/consulting.template')
        self.response.out.write(template.render(self.template_values))

class CivilConstructionPage(_BaseHandler):
    def get(self):
        logging.info('CivilConstructionPage class requested')

        self.template_values['svg']={
        'facebook': facebook_svg,
        'google': google_svg,
        'twitter': twitter_svg
          }

        template = jinja_environment.get_template('views/civil-construction.template')
        self.response.out.write(template.render(self.template_values))

class BuildingPage(_BaseHandler):
    def get(self):
        logging.info('BuildingPage class requested')

        self.template_values['svg']={
        'facebook': facebook_svg,
        'google': google_svg,
        'twitter': twitter_svg
          }

        template = jinja_environment.get_template('views/building.template')
        self.response.out.write(template.render(self.template_values))

class ServicePage(_BaseHandler):
    def get(self):
        logging.info('ServicePage class requested')

        self.template_values['svg']={
        'facebook': facebook_svg,
        'google': google_svg,
        'twitter': twitter_svg
          }

        template = jinja_environment.get_template('views/service.template')
        self.response.out.write(template.render(self.template_values))


class AboutPage(_BaseHandler):
    def get(self):
        logging.info('AboutPage class requested')

        self.template_values['svg']={
        'facebook': facebook_svg,
        'google': google_svg,
        'twitter': twitter_svg
          }

        template = jinja_environment.get_template('views/about.template')
        self.response.out.write(template.render(self.template_values))


class RegisterPage(_BaseHandler):
    @profileauthdecorator.oauth_required
    def get(self):
        logging.info('RegisterPage class requested')
         #-------------------------------------------------------------------
         #Look for existing profile based on User's email
        doctor_key = ndb.Key('Doctor', self.user.email())
        doctor = doctor_key.get()

        self.template_values['svg']={
         'facebook': 'public/svg/facebook.svg'
          } 
        self.template_values['svg1']={
         'google': 'public/svg/google.svg'
          }
        self.template_values['svg2']={
          'twitter': 'twitter.svg'
          }

        if doctor:
            template = jinja_environment.get_template('views/registered.template')
            self.response.out.write(template.render(self.template_values))          

        else: 
            #Profile doesn't yet exist, create a new Doctor with default values
            newKey = ndb.Key("Doctor", self.user.email())
            doctor = models.Doctor(key=newKey)
            #Add the doctor model to our template values for rendering
            self.template_values['doctor'] =doctor
            #--------------------------------------------------------------------   
            template = jinja_environment.get_template('views/register.template')
            self.response.out.write(template.render(self.template_values))         
 
    def post(self):
        logging.info('RegisterPage posted')
        #Look for existing profile based on Users' email
        doctor_key = ndb.Key('Doctor', self.user.email())
        doctor = doctor_key.get()
        if doctor:
            self.redirect('/register')
        if not doctor:
            #Profile doesn't yet exist, create a new Doctor with default values
            doctor = models.Doctor(key=ndb.Key("Doctor",self.user.email()))

        #Update the user controll
        doctor.username =  self.user.email() 
        doctor.notifyEmail = self.request.get('notifyEmail')   
        doctor.bio = self.request.get('bio')
        doctor.designation=self.request.get('designation') 
        doctor.organization=self.request.get('organization') 
        doctor.field=self.request.get('field') 
        doctor.specialization=self.request.get('specialization') 
        doctor.idNumber=int(self.request.get('idNumber'))
        doctor.province=self.request.get('province') 
        doctor.city=self.request.get('city') 
        doctor.gender=self.request.get('gender') 
        doctor.contactNumber=self.request.get('contactNumber') 
        doctor.mobileNumber=self.request.get('mobileNumber') 
                                                                                                                                                                            #Commit our updates to the datastore
        doctor.put()
        self.redirect('/register')

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
      idNumber=ndb.IntegerProperty()
      province=ndb.TextProperty()
      ethnicGroup=ndb.TextProperty()
      city=ndb.TextProperty()
      address=ndb.KeyProperty(repeated=True)
      gender=ndb.TextProperty()
      dateOfBirth=ndb.DateTimeProperty()
      contactNumber=ndb.TextProperty()
      mobileNumber=ndb.TextProperty()
      created = ndb.DateTimeProperty(default=datetime.datetime.now())
      status = ndb.StringProperty(default="pending")

class ManageUsersPage(_BaseHandler):
    @profileauthdecorator.oauth_required
    def get(self):
        logging.info('Manage Users class requested')
         #-------------------------------------------------------------------
         #Look for existing profile based on User's email
            #Add the doctor model to our template values for rendering
        doctors = Doctor.query(Doctor.status=='pending')
        self.template_values['doctors'] =doctors                                                                                                   #--------------------------------------------------------------------   

         
        self.template_values['svg']={
         'facebook': 'public/svg/facebook.svg'
          } 
        self.template_values['svg1']={
         'google': 'public/svg/google.svg'
          }
        self.template_values['svg2']={
          'twitter': 'twitter.svg'
          }
        
        template = jinja_environment.get_template('views/manage-users.template')
        self.response.out.write(template.render(self.template_values)) 

class UserDetailsPage(_BaseHandler):
    @profileauthdecorator.oauth_required
    def get(self):
        logging.info('UserDetailsPage class requested')
         #-------------------------------------------------------------------
         #Look for existing profile based on User's email
        user_email=self.request.get('email')
        logging.info(user_email)
        doctor_key = ndb.Key('Doctor', user_email)
        doctor = doctor_key.get()
        if not doctor:
        #Profile doesn't yet exist, create a new Doctor with default values
           newKey = ndb.Key("Doctor", self.user.email())
           doctor = models.Doctor(key=newKey)
          #Add the doctor model to our template values for rendering
        self.template_values['doctor'] =doctor 
                                                                                                   #--------------------------------------------------------------------   

         
        self.template_values['svg']={
         'facebook': 'public/svg/facebook.svg'
          } 
        self.template_values['svg1']={
         'google': 'public/svg/google.svg'
          }
        self.template_values['svg2']={
          'twitter': 'twitter.svg'
          }
        
        template = jinja_environment.get_template('views/user-details.template')
        self.response.out.write(template.render(self.template_values))
 
    def post(self):
        logging.info('UserDetailsPage posted')
        #Look for existing profile based on Users' email
        user_email=self.request.get('username')
        logging.info(user_email)
        doctor_key = ndb.Key('Doctor', user_email)
        doctor = doctor_key.get()
        
        #Update the user controll
       
        doctor.status=self.request.get('status') 
                                                                                                                                                                            #Commit our updates to the datastore
        doctor.put()
        self.redirect('/manage-users')
class ChatRoomPage(_BaseHandler):
    def get(self):
        logging.info('Chat Room class requested')
        user = users.get_current_user()
        if user:
            user_id = user.user_id()            
            client_auth_token = create_custom_token(user_id)

            self.template_values = {
            'token': client_auth_token,
            'user_id': user_id,
            'nickname':'Tebog The Boss',
            'me': user.user_id()      
             }
             #-------------------------------------------------------------------
             #Look for existing profile based on User's email
            
            template = jinja_environment.get_template('views/chat-room.template')
            self.response.out.write(template.render(self.template_values))         
      
class ProfilePage(_BaseHandler):
    @profileauthdecorator.oauth_required
    def get(self):
        logging.info('ProfilePage class requested')
         #-------------------------------------------------------------------
         #Look for existing profile based on User's email
        doctor_key = ndb.Key('Doctor', self.user.email())
        doctor = doctor_key.get()
        if not doctor:
        #Profile doesn't yet exist, create a new Doctor with default values
           newKey = ndb.Key("Doctor", self.user.email())
           doctor = models.Doctor(key=newKey)
          #Add the doctor model to our template values for rendering
        self.template_values['doctor'] =doctor 
                                                                                                   #--------------------------------------------------------------------   

         
        self.template_values['svg']={
         'facebook': 'public/svg/facebook.svg'
          } 
        self.template_values['svg1']={
         'google': 'public/svg/google.svg'
          }
        self.template_values['svg2']={
          'twitter': 'twitter.svg'
          }
        
        template = jinja_environment.get_template('views/profile.template')
        self.response.out.write(template.render(self.template_values))         
  
    def post(self):
        logging.info('ProfilePage posted')
        #Look for existing profile based on Users' email
        doctor_key = ndb.Key('Doctor', self.user.email())
        doctor = doctor_key.get()
        if not doctor:
            #Profile doesn't yet exist, create a new Doctor with default values
            doctor = models.Doctor(key=ndb.Key("Doctor",self.user.email()))

        #Update the user controll
        doctor.username =  self.user.email() 
        doctor.notifyEmail = self.request.get('notifyEmail')   
        doctor.bio = self.request.get('bio')
        doctor.designation=self.request.get('designation') 
        doctor.organization=self.request.get('organization') 
        doctor.field=self.request.get('field') 
        doctor.specialization=self.request.get('specialization') 
        doctor.idNumber=int(self.request.get('idNumber'))
        doctor.province=self.request.get('province') 
        doctor.city=self.request.get('city') 
        doctor.gender=self.request.get('gender') 
        doctor.contactNumber=self.request.get('contactNumber') 
        doctor.mobileNumber=self.request.get('mobileNumber') 
                                                                                                                                                                            #Commit our updates to the datastore
        doctor.put()
        self.redirect('/profile')

app = webapp2.WSGIApplication([
    ('/admin', MainPage),
    ('/profile', ProfilePage),
    ('/about',AboutPage),
    ('/contacts',ContactsPage),
    ('/news',NewsPage),
    ('/terms-of-use',TermsOfUsePage),
    ('/privacy-policy',PrivacyPolicyPage),
    ('/pee',PeePage),
    ('/consulting',ConsultingPage),
    ('/civil-construction',CivilConstructionPage),
    ('/building',BuildingPage),
    ('/service',ServicePage),
    ('/register',RegisterPage),
    ('/manage-users',ManageUsersPage),
    ('/user-details',UserDetailsPage), 
    ('/chat-room',ChatRoomPage), 
    (profileauthdecorator.callback_path, profileauthdecorator.callback_handler()),    
    ('/', MainPage)
], debug=True)
