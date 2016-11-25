import webapp2
import jinja2
import os
import logging
from models import models
import datetime
import time
import base64
import json

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
    client_email = app_identity.get_service_account_name()

    now = int(time.time())
    # encode the required claims
    # per https://firebase.google.com/docs/auth/server/create-custom-tokens
    payload = base64.b64encode(json.dumps({
        'iss': client_email,
        'sub': client_email,
        'aud': _IDENTITY_ENDPOINT,
        'uid': uid,  # the important parameter, as it will be the channel id
        'iat': now,
        'exp': now + (valid_minutes * 60),
         }))
    # add standard header to identify this as a JWT
    header = base64.b64encode(json.dumps({'typ': 'JWT', 'alg': 'RS256'}))
    to_sign = '{}.{}'.format(header, payload)
    # Sign the jwt using the built in app_identity service
    return '{}.{}'.format(to_sign, base64.b64encode(
        app_identity.sign_blob(to_sign)[1]))

class _BaseHandler(webapp2.RequestHandler):
    def initialize(self, request, response):
        super(_BaseHandler, self).initialize(request, response)

        self.user = users.get_current_user()
        
             
        if self.user:
            doctor_key = ndb.Key('Doctor', self.user.email())
            doctor = doctor_key.get()
            if doctor:
                registered=True
            else:
                registered=False
            logging.info("User ID : "+self.user.user_id()) 
            imgUrl=self.getUserImg()
            self.template_values = {
                'user': self.user,
                'is_admin': users.is_current_user_admin(),
                'logout_url': users.create_logout_url('/'),
                'imgUrl':imgUrl,
                'diplayName':self.getUserDisplayName(),
                'registered':registered
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
    @profileauthdecorator.oauth_required
    def getUserDisplayName(self):
       
        auth_http = profileauthdecorator.http()
        logging.info(auth_http)
        service = build('plus', 'v1', http=auth_http)
        people_resource = service.people()
        people_document = people_resource.get(userId='me').execute()
        displayName=people_document['displayName']
        return displayName


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
            logging.info('User Id @12345 is : '+user_id)         
            client_auth_token = create_custom_token(user_id)
            logging.info('User display name : ')
            logging.info(self.getUserDisplayName())
            self.template_values['chat'] = {
            'token': client_auth_token,
            'user_id': user_id,
            'displayName':self.getUserDisplayName(),
            'me': user.user_id(),
            'email': user.email(),   
             }
             #-------------------------------------------------------------------
             #Look for existing profile based on User's email
            self.template_values['svg']={
               'facebook': 'public/svg/facebook.svg'
            } 
            self.template_values['svg1']={
               'google': 'public/svg/google.svg'
            }
            self.template_values['svg2']={
               'twitter': 'twitter.svg'
            }
            
            template = jinja_environment.get_template('views/chat-room.template')
            self.response.out.write(template.render(self.template_values)) 
    @profileauthdecorator.oauth_required
    def getUserDisplayName(self):
       
        auth_http = profileauthdecorator.http()
        logging.info(auth_http)
        service = build('plus', 'v1', http=auth_http)
        people_resource = service.people()
        people_document = people_resource.get(userId='me').execute()
        displayName=people_document['displayName']
        return displayName      
      
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
