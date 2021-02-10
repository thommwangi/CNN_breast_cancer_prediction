from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField
from wtforms.validators import InputRequired, Length, EqualTo, ValidationError
from application import User
from application import Patient
from passlib.hash import pbkdf2_sha256


#custom validation function to validate user login
def invalid_credentials(form, field):
    """ Username and Password checker """
    username_entered = form.username.data
    password_entered = field.data 

    #checking if credentials are valid
    user_object = User.query.filter_by(username=username_entered).first()
    if user_object is None:
         raise ValidationError("Username or Password is incorrect")
    elif not pbkdf2_sha256.verify(password_entered,user_object.password):
         raise ValidationError("Username or Password is incorrect")


class RegistrationForm(FlaskForm):
    """ Registration Form """

    username = StringField('username_label', validators=[InputRequired(message="Username required"),
    Length(min=4, max=25, message="Username must be between 4 and 25 characters")])

    password = PasswordField('password_label', validators=[InputRequired(message="Password required"),
    Length(min=4, max=25, message="Password must be between 4 and 25 characters")])

    confirm_pwd = PasswordField('confirm_pwd_label', validators=[InputRequired(message="Password required"), 
    EqualTo('password', message="Passwords must match")])

    submit_button = SubmitField('Create')

    #custom validators
    def validate_username(self, username):
        #checking if username already exists 
        user_object = User.query.filter_by(username=username.data).first()
        if user_object:
            raise ValidationError("Username already exists. Select a different username")


class LoginForm(FlaskForm):
    """ Login form """

    username = StringField('username_label', validators=[InputRequired(message="Username required")])
    password = PasswordField('password_label', validators=[InputRequired(message="Password required"), invalid_credentials])#, invalid_credentials

    submit_button = SubmitField('Login')


class ImagesForm(FlaskForm):
    """ Images form """

    patientname = StringField('patientname_label', validators=[InputRequired(message="Patient name required")])
    hospital = StringField('hospital_label', validators=[InputRequired(message="Hospital name required")])
    gender = StringField('gender_label', validators=[InputRequired(message="Patient gender required")])
    phoneno = IntegerField('phoneno_label', validators=[InputRequired(message="Patient mobile number required")])
    patientname = StringField('patientname_label', validators=[InputRequired(message="Patient name required")])
    

    submit_button = SubmitField('Predict')