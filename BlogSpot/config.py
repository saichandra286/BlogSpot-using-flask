import os
basedir = os.path.abspath(os.path.dirname(__file__))


WTF_CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

OPENID_PROVIDERS = [
    {'name': 'Google', 'url': 'https://www.google.com/accounts/o8/id'},
    {'name': 'Yahoo', 'url': 'https://me.yahoo.com/<username>'},
    {'name': 'AOL', 'url': 'http://openid.aol.com/<username>'},
    {'name': 'Flickr', 'url': 'http://www.flickr.com/<username>'},
    {'name': 'MyOpenID', 'url': 'https://www.myopenid.com'},
    {'name': 'Facebook', 'url': 'https://www.facebook.com/<username>'}]

if os.environ.get('DATABASE_URL') is None:
	SQLALCHEMY_DATABASE_URI = ('sqlite:///' + os.path.join(basedir, 'app.db') + '?check_same_thread=False')
else:
	SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
SQLALCHEMY_MIGRATE_REPO  = os.path.join(basedir, 'db_repository')
SQLALCHEMY_RECORD_QURIES = True
WHOOSH_BASE = os.path.join(basedir, 'search.db')

WHOOSH_ENABLED = os.environ.get('HEROKU') is None

MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = "saic34@gmail.com"
MAIL_PASSWORD = "9052476728"

# administrator list
ADMINS = ['saihero225@gmail.com'] 


lang={
	'en':'English',
	'es':'Español'
}

MS_TRANSLATOR_CLIENT_ID = ''
MS_TRANSLATOR_CLIENT_SECRET =''

# pagination
POSTS_PER_PAGE = 3 

MAX_SEARCH_RESULTS = 50
