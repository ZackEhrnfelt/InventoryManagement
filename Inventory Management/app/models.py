from app import app
from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import ForeignKey, Table
from sqlalchemy.sql import text
from sqlalchemy.orm import relationship

from datetime import datetime
import sys

if sys.version_info >= (3, 0):
    enabled_search = False
else:
    enabled_search = True
    import flask_whooshalchemy as whooshalchemy

class Blog(db.Model):
    __searchable__ = ['body']

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'))

    def __repr__(self):
        return '<Blog %r>' % (self.body)

if enabled_search:
    whooshalchemy.whoosh_index(app, Blog)

class User(UserMixin, db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=False)
    email = db.Column(db.String(64), unique=True)
    role = db.Column(db.String(64))
    userdescription = db.Column(db.String(1028))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    password_hash = db.Column(db.String(256), unique=True)

    def set_password(self, password):
        #Stores hashed password in database
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def blog_posts(self):
            return Post.query.order_by(Post.timestamp.desc())

class Items(db.Model):
    __tablename__ = 'Items'
    itemid = db.Column(db.Integer, primary_key=True)
    itemname = db.Column(db.String(32), unique=False)
    itemdescription = db.Column(db.String(1028), unique=False)
    

class Post(db.Model):
    __tablename__ = 'Post'

    id = db.Column(db.Integer, primary_key = True)
    Creator = db.Column(db.Integer, db.ForeignKey('User.id'))
    Post = db.Column(db.Text)
    
    post_id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, ForeignKey('User.id'), nullable=False)
    # forum_id = db.Column(db.Integer, ForeignKey('Item.id'), nullable=False)
    
class Comment(db.Model):
    __tablename__ = 'comment'
    comment_id = db.Column(db.Integer, primary_key = True)
    date = db.Column(db.DateTime, nullable = True)
    # user_id = db.Column(db.String(64), db.ForeignKey('User.username'), nullable = True)
    # post_id = db.Column(db.Integer, db.ForeignKey('Items.itemid'), nullable=True)
    content = db.Column(db.String(128), default=datetime.utcnow)
       

class InventoryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    voltage = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(256), nullable=False)
    manufacturer = db.Column(db.String(64), nullable=False)
    item_number = db.Column(db.String(64), nullable=False)
    image = db.Column(db.String(256), nullable=False)
    location = db.Column(db.String(64), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    created_on = db.Column('created_on', db.DateTime, default=datetime.utcnow)
    updated_on = db.Column('updated_on', db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, ForeignKey('User.id'))
    user = db.relationship("User", backref=db.backref("user", uselist=False))

  
@login.user_loader
def load_user(id):
    return db.session.query(User).get(int(id))
