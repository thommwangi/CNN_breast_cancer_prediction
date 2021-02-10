#MODEL IMPORTS
import os
import io
import cv2
import tensorflow as tf
import keras
from keras import backend as K
from keras.preprocessing.image import ImageDataGenerator, img_to_array
from keras.models import Sequential
from keras.models import load_model
import numpy as np
from keras.preprocessing import image                  
import os, os.path
import imageio
from sklearn.metrics import confusion_matrix, f1_score
from sklearn.utils import class_weight
from PIL import Image



from flask_migrate import Migrate
from flask  import Flask, render_template, redirect, url_for, flash, request
from wtforms_fields import *
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, current_user, login_required, logout_user
import os
#from passlib.hash import pbkdf2_sha256
#from models import *


app=Flask(__name__)
app.secret_key = os.environ.get('SECRET')
ENV = 'dev'
UPLOAD_FOLDER=r'C:\Users\mwangit\Desktop\projects\webapp\static\uploaded_images'

#configuring user sessions(Flask_login)
login = LoginManager(app)
login.init_app(app)


##############################################################################################
#LOADING THE MODEL
def sensitivity(y_true, y_pred):
  true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
  possible_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
  return true_positives / (possible_positives + K.epsilon())

def specificity(y_true, y_pred):
  true_negatives = K.sum(K.round(K.clip((1-y_true) * (1-y_pred), 0, 1)))
  possible_negatives = K.sum(K.round(K.clip(1-y_true, 0, 1)))
  return true_negatives / (possible_negatives + K.epsilon())

def fmed(y_true, y_pred):
  spec = specificity(y_true, y_pred)
  sens = sensitivity(y_true, y_pred)
  fmed = 2 * (spec * sens)/(spec+sens+K.epsilon())
  return fmed

def f1(y_true, y_pred):
  true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
  possible_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
  predicted_positives = K.sum(K.round(K.clip(y_pred, 0, 1)))
  precision = true_positives / (predicted_positives + K.epsilon())
  recall = true_positives / (possible_positives + K.epsilon())
  f1_val = 2*(precision*recall)/(precision+recall+K.epsilon())
  return f1_val


def get_model():
      global model
      dependancies={
          'sensitivity':sensitivity,
          'specificity':specificity,
          'fmed':fmed,
          'f1':f1
      }
      model = tf.keras.models.load_model('3-conv-3-dense-64-featDet-CNN.h5', custom_objects=dependancies, compile=True, options=None)
      print("Model loaded successfully!")


def preprocessImage(image_location):
    image = tf.keras.preprocessing.image.load_img(image_location, color_mode="rgb",target_size=(150,150))
    input_arr = keras.preprocessing.image.img_to_array(image)
    input_arr = np.array([input_arr])  # Convert single image to a batch.
    return input_arr
    # if image.mode != "RGB":
    #     image = image.convert("RBG")
    # image=image.resize(target_size)
    # image = img_to_array(image)
    # image = np.expand_dims(image, axis=0)

    #return image


print(" * Loading model.... ")
get_model()



# if ENV == 'dev':
#     app.debug=True
#     app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:@127.0.0.1/mammodb'
# else:
app.debug=False
#production db
app.config['SQLALCHEMY_DATABASE_URI']=os.environ.get('DATABASE_URL')
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#db object
db= SQLAlchemy(app)


#User table
class User(UserMixin, db.Model):
    """ User model """
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25),unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)

    def __init__(self,username,password):
        self.username=username
        self.password=password


#Patients Table

class Patient(UserMixin, db.Model):
    """ Patient model """
    __tablename__ = "patients"
    id = db.Column(db.Integer, primary_key=True)
    patientname = db.Column(db.String(25), nullable=False)
    hospital = db.Column(db.String(40), nullable=False)
    gender = db.Column(db.String(25), nullable=False)
    phoneno = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(200), nullable=False)
    prediction = db.Column(db.String(25), nullable=False)

    def __init__(self,patientname,hospital,gender,phoneno,image,prediction):
        self.patientname=patientname
        self.hospital=hospital
        self.gender=gender
        self.phoneno=phoneno
        self.image=image
        self.prediction=prediction
    def __repr__(self):
        return f"<Patient {self.name}>"
#db.init_app(app)
#migrate = Migrate(app, db)


#loading the user data
@login.user_loader
def load_user(id):
    return User.query.get(int(id))



@app.route("/", methods=['GET','POST'])
def index():

    reg_form = RegistrationForm()
    #updates the db if validation is successful
    if reg_form.validate_on_submit():
        
        username = reg_form.username.data
        password = reg_form.password.data

        #hashed password
        hashed_pwd = pbkdf2_sha256.hash(password)

        

        #inserting data to db
        user = User(username=username, password=hashed_pwd)
        db.session.add(user)
        db.session.commit()

        flash("Registered successfuly. Please login", 'success')

        return redirect(url_for('login'))

    return render_template("index.html", form=reg_form)


#login route
@app.route("/login", methods=['GET','POST'])

def login():

    login_form=LoginForm()

    #allow login if validation successful
    if login_form.validate_on_submit():
        user_object = User.query.filter_by(username=login_form.username.data).first()
        login_user(user_object)
        
        return redirect(url_for('images'))
        
    
    return render_template("login.html", form=login_form)



#protected routes
CATEGORIES=['Benign','Malignant']
@app.route("/images", methods=['GET', 'POST'])
#@login_required
def images():

    if not current_user.is_authenticated:
        flash("Please login to access this page", 'warning')
        return redirect (url_for('login'))

    if request.method == 'POST':
        image_file = request.files["image"]
        if image_file:
            image_location = os.path.join(UPLOAD_FOLDER, image_file.filename)
            image_file.save(image_location)
            processed_image=preprocessImage(image_location)
            pred = model.predict(processed_image)
            
            #print(CATEGORIES[int(pred[0][0])])
            pred = CATEGORIES[int(pred[0][0])]

            patientname=request.form.get("patientname")
            hospital=request.form.get("hospital")
            gender=request.form.get("gender")
            phoneno=request.form.get("phoneno")
            image=image_location
            prediction=pred

            #storing in db
            patient = Patient(patientname=patientname, hospital=hospital, gender=gender, phoneno=phoneno, image=image_location, prediction=pred)
            db.session.add(patient)
            db.session.commit()
            #flash("Data saved.", 'success')

            return render_template("images.html", prediction=pred, image_loc=image_file.filename)

    return render_template("images.html", prediction=0, image_loc=None)


@app.route("/patients", methods=['GET','POST'])
def patients():
    if not current_user.is_authenticated:
        flash("Please login to access this page", 'warning')
        return redirect (url_for('login'))

    patient_object = Patient.query.all()
    return render_template("patients.html", patient_object=patient_object)
    




@app.route("/logout", methods=['GET'])
def logout():
    logout_user()
    flash("Successfuly logged out", 'success')
    return redirect(url_for('login'))



if __name__ == '__main__': 
    app.run(debug=True)