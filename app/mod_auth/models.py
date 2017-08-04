# Import the database object (db) from the main application module
# We will define this inside /app/__init__.py in the next sections.
from app import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash

from flask.ext.login import UserMixin

@login_manager.user_loader
def get_user(ident):
    return User.query.get(int(ident))

# Forward declare the way that we'll keep track of who has what
#cards = db.Table('cards',
#        db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
#        db.Column('card_id', db.Integer, db.ForeignKey('card.id')),
#        db.Column('num_normal', db.Integer),
#        db.Column('num_holo', db.Integer)
#)

# Define a base model for other database tables to inherit
class Base(db.Model):

    __abstract__  = True

    id            = db.Column(db.Integer, primary_key=True)
    date_created  = db.Column(db.DateTime,  default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime,  default=db.func.current_timestamp(),
                                           onupdate=db.func.current_timestamp())

# Define a User model
class User(Base, UserMixin):

    __tablename__ = 'user'

    # User Name
    name    = db.Column(db.String(128),  nullable=False,
					    unique=True)
    password = db.Column(db.String(192),  nullable=False)

    cards = db.relationship('UserCards',
	backref = 'user', cascade='all, delete-orphan', lazy='dynamic')

    # New instance instantiation procedure
    def __init__(self, name, password):

        self.name     = name
        self.password = generate_password_hash(password)
    
    def __repr__(self):
        return '<User %r>' % (self.name)

    def is_active(self):
        return True

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    @classmethod
    def get(cls, id):
        return cls.user_database.get(id)
