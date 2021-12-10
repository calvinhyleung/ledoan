from flask_login import UserMixin
from mongoengine.fields import ImageField
from datetime import datetime
from . import db, login_manager
from . import config
from enum import Enum
# from .utils import current_time
import base64
import io

@login_manager.user_loader
def load_user(user_id):
    return User.objects(username=user_id).first()

class User(db.Document, UserMixin):
    username = db.StringField(required=True, unique=True)
    email = db.EmailField(required=True, unique=True)
    password = db.StringField(required=True)

    # Returns unique string identifying our object
    def get_id(self):
        return self.username

class Product(db.Document):
    name = db.StringField(required=True, unique=True)
    price = db.FloatField(required=True)
    description = db.StringField(required=True)
    ingredients = db.StringField(required=False)
    amount = db.IntField(required=True)
    image = db.ImageField(unique=False, required=True)
    limit = db.IntField(required=True) 
    def get_limit(self):
        return self.limit
    def get_b64_img(self):
        bytes_im = io.BytesIO(self.image.read())
        image = base64.b64encode(bytes_im.getvalue()).decode()
        return image
    def get_name(self):
        return self.name

class Status(Enum):
    PENDING = 'Pending'
    CONFIRMED = 'Confirmed'
    DECLINED = 'Declined'
    PAID = 'Paid'
    PICKEDUP = 'Picked-up'

class StatusColor(Enum):
    PENDING = "badge badge-primary"
    CONFIRMED = "badge badge-secondary"
    DECLINED = "badge badge-danger"
    PAID = "badge badge-success"
    PICKEDUP = "badge badge-light"

class Reservation(db.Document):
    user = db.ReferenceField(User)
    product = db.ReferenceField(Product)
    amount = db.IntField(required=True)
    status = db.StringField(required=True)
    def get_amount(self):
        return self.amount