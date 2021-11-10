from flask import Flask, render_template, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from wtforms.validators import DataRequired, Email
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.orm import Session
from flask_cors import CORS, cross_origin
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import* 
from config import Configob
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import request,redirect,url_for,flash
from flask_toastr import Toastr
from werkzeug.utils import secure_filename
import logging
import boto3
from botocore.exceptions import ClientError
from botocore.client import Config
from datetime import date
import datetime
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from flask_login import LoginManager
from flask_login import login_user,login_required,current_user,logout_user



app = Flask(__name__)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
app.config.from_object(Configob)
toastr = Toastr(app)
DB_URI = app.config['SQLALCHEMY_DATABASE_URI']
engine = create_engine(DB_URI)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "home"
login_manager.login_message = u"Please login to access this page."
login_manager.login_message_category = "info"


class UsersModel(db.Model):
    __tablename__ = 'account'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(),unique=True)
    password = db.Column(db.String())
    authenticated = db.Column(db.Boolean, default=False)
    last_message_read_time = db.Column(db.DateTime)

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.id

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False

    def __init__(self, email, password, authenticated):
        self.email=email
        self.password=password
        self.authenticated=authenticated
        

    def __repr__(self):
        return f"<User {self.email}>"

class QuotesModel(db.Model):
    __tablename__ = 'quotes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    phone_number = db.Column(db.String())
    email = db.Column(db.String())
    message = db.Column(db.String())
    date = db.Column(db.DateTime)

    def __init__(self, name, email, phone_number, message, date):
        
        self.name=name
        self.phone_number=phone_number
        self.email=email
        self.message=message
        self.date=date
        
    def __repr__(self):
        return f"<Quote {self.name}>"

class Photo(db.Model):
    __tablename__ = 'photo'

    photo_id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String())
    detail = db.Column(db.String())
    file_path = db.Column(db.String(150), nullable=False)

    def __init__(self,file_path, title, detail):
        self.title=title
        self.detail=detail
        self.file_path=file_path
       
    def __repr__(self):
        return f"<Photo {self.file_path}>"


class ContactModel(db.Model):
    __tablename__ = 'contact_us'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    phone_number = db.Column(db.String())
    email = db.Column(db.String())
    subject = db.Column(db.String())
    message = db.Column(db.String())
    date = db.Column(db.DateTime)

    def __init__(self, name, email, phone_number,subject, message, date):
        
        self.name=name
        self.phone_number=phone_number
        self.email=email
        self.subject=subject
        self.message=message
        self.date=date
        
    def __repr__(self):
        return f"<Quote {self.name}>"

# ContactModel.__table__.drop(engine)
db.create_all()
db.session.commit()

CORS(app, support_credentials=True)
Base = automap_base()
Base.prepare(engine, reflect=True)
Accounts = Base.classes.account
Quotes = Base.classes.quotes
Photos = Base.classes.photo
Contact_us = Base.classes.contact_us
session = Session(engine)
metadata = MetaData(engine)
# sess=Session(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower()\
                               in app.config['ALLOWED_EXTENSIONS']

s3_obj = boto3.client('s3',
                      aws_access_key_id='AKIA3ILV3U7F36VT4QNE',
                      aws_secret_access_key="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",
                      config=Config(region_name = 'us-east-2',
                                    signature_version='s3v4'))

def upload_file_to_s3(s3_file_path, file, bucket_name):
    s3_obj.upload_fileobj(
            file,
            bucket_name,
            s3_file_path,
            
    )

def create_presigned_url(bucket_name, object_name, expiration=8600):
    try:
        response = s3_obj.generate_presigned_url(
                                        'get_object',
                                        Params={
                                            'Bucket': bucket_name,
                                            'Key': object_name
                                        },
                                        ExpiresIn=expiration)
    except ClientError as exc:
        logging.error(exc)
        return None

    # The response contains the presigned URL
    return response

def delete_file_from_s3(bucket_name, s3_file_path):
    try:
        s3_obj.delete_object(Bucket=bucket_name, Key=s3_file_path)
    except ClientError as exc:
        logging.error(exc)
        return None


@login_manager.user_loader
def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return UsersModel.query.get(int(user_id))

@app.route("/")
def home():
    photos = Photo.query.all()
    bucket_name ="land-site-images"
    url_list = []
        # fetches urls of all S3 pictures
    for photo in photos:
            url = create_presigned_url(bucket_name, photo.file_path)
            url_list.append(url)
    photolist=zip(url_list,photos)        
    return render_template("home.html",photos=photolist)

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/services")
def services():
    return render_template("services.html")  

@app.route("/projects")
def projects():
    return render_template("projects.html") 

@app.route("/about")
def about():
    return render_template("about.html") 

@app.route("/images")
@login_required
def images():
    last_read_time = UsersModel.last_message_read_time or datetime(1900, 1, 1)
    count= QuotesModel.query.filter(QuotesModel.date > last_read_time).count()
    last_read_time = UsersModel.last_message_read_time or datetime(1900, 1, 1)
    countmessage= ContactModel.query.filter(ContactModel.date > last_read_time).count()
    photos = Photo.query.all()
    bucket_name ="land-site-images"
    url_list = []
    id_list = []
    title = []
    detail = []
        # fetches urls of all S3 pictures
    for photo in photos:
            url = create_presigned_url(bucket_name, photo.file_path)
            url_list.append(url)
    photolist=zip(url_list,photos)
    return render_template("images.html", photos=photolist ,new_messages=count , countmessage=countmessage)

@app.route("/logout")
@login_required
def logout():
    user = current_user
    user.authenticated = False
    db.session.add(user)
    db.session.commit()
    logout_user()
    return redirect(url_for('home'))

###Admin Service### 

@app.route('/register', methods=["GET", "POST"])
@login_required
def register():
    email = request.form['email']
    password = request.form['password']
    password_hash = generate_password_hash(password)
    existing_user = UsersModel.query.filter_by(email=email).first()
    account = Table('account', metadata, autoload=True)
    if existing_user is None:
        engine.execute(account.insert(),email=email, password=password_hash)
        flash('New Admin added successfully', 'success')
        return redirect(url_for('list_admin'))
        users =  UsersModel.query.all()
    else:
        flash('Fail, Admin with that email address exist', 'info')
        return  redirect(url_for('images'))
        

@app.route('/login', methods=["GET", "POST"])
def login():
    email_entered =  request.form['email']
    password_entered =request.form['password']
    user = UsersModel.query.filter_by(email=email_entered).first()
    if user is not None and check_password_hash(user.password, password_entered):
        user.authenticated = True
        db.session.add(user)
        db.session.commit()
        login_user(user, remember=True)
        return  redirect(url_for('images'))
    flash('login fail, check your password and email entered', 'warning')
    return  redirect(url_for('home'))

@app.route('/list_admin',  methods=["GET", "POST"]) 
@login_required
def list_admin():
        users =  UsersModel.query.all()
        return render_template('adminlist.html', users=users)

@app.route('/delete', methods = ['GET', 'POST'])
@login_required
def delete():
        id_entered =  request.form['id']
        users = UsersModel.query.get(id_entered)
        db.session.delete(users)
        db.session.commit()
        flash('Admin deleted successfully', 'success')
        return redirect(url_for('list_admin'))
     
@app.route('/edit_user', methods = ['GET', 'POST'])
@login_required
def edit_user():
        id_entered =  request.form['id']
        password_entered =request.form['password']
        users = UsersModel.query.get(id_entered)
        password_hash = generate_password_hash(password_entered)
        users.password=password_hash    
        db.session.commit()
        flash('Admin password successfully changed', 'success')
        return redirect(url_for('list_admin'))

 #### Discount Service ####
@app.route('/add_discount', methods=["GET", "POST"])
def add_discount():
    name = request.form['name']
    phone_number = request.form['phone_number']
    email = request.form['email']
    message = request.form['message']
    now =datetime.datetime.utcnow()
    quotes = Table('quotes', metadata, autoload=True)
    engine.execute(quotes.insert(),name=name, phone_number=phone_number, email=email, message=message, date=now)
    flash('Discount successfully submitted', 'success')
    return  redirect(url_for('home'))
    

@app.route('/list_discount',  methods=['GET', 'POST'])
@login_required
def list_discount():
        last_read_time = UsersModel.last_message_read_time or datetime(1900, 1, 1)
        countmessage= ContactModel.query.filter(ContactModel.date > last_read_time).count()
        #current_user.last_message_read_time = datetime.datetime.utcnow()
        db.session.commit()
        discounts =  QuotesModel.query.all()
        return render_template('list_discount.html',discounts=discounts, countmessage=countmessage)

@app.route('/view_discount<id>', methods=['GET', 'POST'])
def view_discount(id):
        discountview=QuotesModel.query.filter_by(id=id).first()
        if discountview is None:
            flask('No discount exist this id', 'info')
            return redirect(url_for('list_discount'))
        else:
            return render_template('discountview.html', discountview=discountview)

@app.route('/delete_discount', methods=['GET', 'POST'])
@login_required
def delete_discount():
        id_entered=request.form['id']
        discountview=QuotesModel.query.get(id_entered)
        db.session.delete(discountview)
        db.session.commit()
        flash('Discount deleted successfully', 'success')
        return redirect(url_for('list_discount'))

### Picture Upload Service ###

@app.route("/upload", methods=['POST','GET'])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files['file']
        title = request.form['title']
        detail = request.form['detail']
        if file.filename == '':
            print('No selected file')
            return redirect(url_for('images'))
 
        if file and allowed_file(file.filename):
            file_name = secure_filename(file.filename)
            file_path = '{}/{}'.format( title, file_name)

            im = Image.open(file)
            width, height = im.size
            draw = ImageDraw.Draw(im)
            text = "Golden Let Estate And Investment LTD"
            font = ImageFont.truetype('arial.ttf', 36)
            textwidth, textheight = draw.textsize(text, font)

            # calculate the x,y coordinates of the text
            margin = 10
            x = width - textwidth - margin
            y = height - textheight - margin

            # draw watermark in the bottom right corner
            draw.text((x, y), text, font=font)

            # create a BytesIO object
            im_io = BytesIO() 
            # save image to BytesIO object
            im.save(im_io, 'JPEG', quality=30) 
            # create a django-friendly Files object
            new_file = im_io.getvalue()

            # Upload to s3
            upload_file_to_s3(file_path,  BytesIO(new_file), "land-site-images")

            # Commit the additions
            photo = Table('photo', metadata, autoload=True)
            engine.execute(photo.insert(),title=title, detail=detail, file_path=file_path)
            db.session.commit()
            flash('File uploaded successfully.', "success")
            return  redirect(url_for('images'))

@app.route('/delete_photo<id>', methods=['GET', 'POST'])
@login_required
def delete_photo(id):
    # if session['logged_in']:
        onephoto=Photo.query.filter_by(photo_id=id).first()
        if onephoto is not None:
            bucket_name ="land-site-images"
            delete_file_from_s3(bucket_name,onephoto.file_path)
            db.session.delete(onephoto)
            db.session.commit()
            flash('Photo deleted successfully', 'success')
            return  redirect(url_for('images'))
        else:
            flash('No photo such id found', 'info')
            return  redirect(url_for('images'))
   
@app.route('/view_photo<id>', methods=['GET', 'POST'])
def view_photo(id):
    # if session['logged_in']:
        photoview=Photo.query.filter_by(photo_id=id).first()
        if photoview is None:
            flask('No photo exist this id', 'info')
            return redirect(url_for('home'))
        else:
            print(photoview)
            bucket_name ="land-site-images"
            url_list = []
            # fetches urls of all S3 pictures
            url = create_presigned_url(bucket_name, photoview.file_path)
            #photolist=zip(url_list,photoview)
            return render_template('photo-detail.html', photo=url, photoview=photoview)



### Contact Us Services ###
@app.route('/add_message', methods=["GET", "POST"])
def add_message():
    name = request.form['name']
    phone_number = request.form['phone_number']
    email = request.form['email']
    subject = request.form['subject']
    message = request.form['message']
    now =datetime.datetime.utcnow()
    contact_us = Table('contact_us', metadata, autoload=True)
    engine.execute(contact_us.insert(),name=name, phone_number=phone_number, email=email, subject=subject, message=message, date=now)
    flash('Message successfully submitted', 'success')
    return  redirect(url_for('contact'))

@app.route('/list_messages',  methods=['GET', 'POST'])
@login_required
def list_messages():
        current_user.last_message_read_time = datetime.datetime.utcnow()
        db.session.commit()
        messages =  ContactModel.query.all()
        return render_template('list_message.html',messages=messages)

@app.route('/view_message<id>', methods=['GET', 'POST'])
def view_message(id):
        messageview=ContactModel.query.filter_by(id=id).first()
        if messageview is None:
            flash('No message exist this id', 'info')
            return redirect(url_for('list_messages'))
        else:
            return render_template('messageview.html', messageview=messageview)

@app.route('/delete_message', methods=['GET', 'POST'])
@login_required
def delete_message():
        id_entered=request.form['id']
        messageview=ContactModel.query.get(id_entered)
        db.session.delete(messageview)
        db.session.commit()
        flash('Message deleted successfully', 'success')
        return redirect(url_for('list_messages'))


if __name__ == "__main__":
    app.run(debug=False)