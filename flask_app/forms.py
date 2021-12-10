from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from mongoengine.fields import ImageField
from werkzeug.utils import secure_filename
from wtforms import StringField, IntegerField, SubmitField, TextAreaField, PasswordField, FloatField,  SelectField
from wtforms.validators import (
    InputRequired,
    DataRequired,
    NumberRange,
    Length,
    Email,
    EqualTo,
    ValidationError,
    Regexp,
)
import re
from .models import User, Product

class RegistrationForm(FlaskForm):
    username = StringField(
        "Username", validators=[InputRequired(), Length(min=1, max=40)]
    )
    email = StringField("Email", validators=[InputRequired(), Email()])
    password = PasswordField("Password", validators=[
        InputRequired(), 
        Length(min=8, max=32), 
        Regexp('^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{8,32}$'),
    ])
    confirm_password = PasswordField(
        "Confirm Password", validators=[InputRequired(), EqualTo("password")]
    )
    submit = SubmitField("Sign Up")
    def validate_username(self, username):
        user = User.objects(username=username.data).first()
        if user is not None:
            raise ValidationError("Username is taken")

    def validate_email(self, email):
        user = User.objects(email=email.data).first()
        if user is not None:
            raise ValidationError("Email is taken")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Login")

class UpdateUsernameForm(FlaskForm):
    username = StringField(
        "Username", validators=[InputRequired(), Length(min=1, max=40)]
    )
    submit = SubmitField("Update Username")

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.objects(username=username.data).first()
            if user is not None:
                raise ValidationError("That username is already taken")

class ReservationForm(FlaskForm):
    amount = SelectField("Amount", coerce=int)
    submit = SubmitField("Reserve")

class AddProductForm(FlaskForm):
    name = StringField("Name", validators=[InputRequired()])
    price = FloatField("Price", validators=[InputRequired()])
    description = StringField("Description", validators=[InputRequired()])
    ingredients = StringField("Ingredients", validators=[InputRequired()])
    amount = IntegerField("Amount", validators=[InputRequired()])
    limit = IntegerField("Limit", validators=[InputRequired()])
    image = FileField('Image', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png'], 'Images Only!')
    ])
    submit = SubmitField("Add Product")

class ChangeStatusForm(FlaskForm):
    status = SelectField("Status", choices=[('Pending', 'Pending'), ('Confirmed', 'Confirmed'), ('Declined', 'Declined'), ('Paid', 'Paid'), ('Picked-up', 'Picked-up')])
    submit = SubmitField("Change")