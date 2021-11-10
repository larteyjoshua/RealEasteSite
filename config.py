
import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Configob(object):
	 DEBUG = False
	 SQLALCHEMY_TRACK_MODIFICATIONS =False
	 SECRET_KEY = os.urandom(24)
	 # SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
	 SQLALCHEMY_DATABASE_URI= "postgres://myctgwdfvnbysm:0269952a3cdd343446b72f891f0ecbf28a5bcf2ca0c1a5f780d33f13a6e1f802@ec2-3-208-168-0.compute-1.amazonaws.com:5432/d7a73r7l23sp65"
	 ALLOWED_EXTENSIONS = ('png', 'jpg', 'jpeg') 
	 # These values are used for S3(object storage) connection
	 # S3_KEY = "AKIA3ILV3U7F36VT4QNE"
	 # S3_SECRET = "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"
	 # S3_BUCKET ="land-site-images"
	 # S3_KEY = os.environ.get('S3_KEY')
	 # S3sss_SECRET = os.environ.get('S3_SECRET')
	 # S3_BUCKET = os.environ.get('S3_BUCKET')