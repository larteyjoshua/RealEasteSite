
import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Configob(object):
	 DEBUG = False
	 SQLALCHEMY_TRACK_MODIFICATIONS =False
	 SECRET_KEY = os.urandom(24)
	 # SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
	 SQLALCHEMY_DATABASE_URI= ""
	 ALLOWED_EXTENSIONS = ('png', 'jpg', 'jpeg') 
	 # These values are used for S3(object storage) connection
	 # S3_KEY = os.environ.get('S3_KEY')
	 # S3sss_SECRET = os.environ.get('S3_SECRET')
	 # S3_BUCKET = os.environ.get('S3_BUCKET')
