# Import the database object (db) from the main application module
# We will define this inside /app/__init__.py in the next sections.
from app import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash

from flask.ext.login import UserMixin

# Define a base model for other database tables to inherit
class Base(db.Model):

    __abstract__  = True

    id            = db.Column(db.Integer, primary_key=True)
    date_created  = db.Column(db.DateTime,  default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime,  default=db.func.current_timestamp(),
                                           onupdate=db.func.current_timestamp())

# Define a Card model
class Card(Base):

	__tablename__ = 'card'

	name    = db.Column(db.String(128),  nullable=False,
					    unique=True)
	description = db.Column(db.String(512),  nullable=False)
	holoAllowed = db.Column(db.Boolean)
	holoAlways  = db.Column(db.Boolean)
	imageName   = db.Column(db.String(10), nullable=False,
						unique=True)
	retired     = db.Column(db.Boolean)
	backgroundColor = db.Column(db.String(7))

	# New instance instantiation procedure
	def __init__(	self,
			name,
			description,
			imageName,
			backgroundColor = '#ddd596',
			holoAllowed = False,
			holoAlways = False,
			retired = False):

		self.name     = name
		self.description = description
		self.imageName = imageName
		self.backgroundColor = backgroundColor
		self.holoAllowed = holoAllowed
		self.holoAlways = holoAlways
		self.retired = retired
    
	def __repr__(self):
		return '<User %r>' % (self.name)

class UserCards(Base):
	__tablename__ = 'user_cards'
	user_id	= db.Column(db.Integer, db.ForeignKey('user.id'))
	card_id	= db.Column(db.Integer, db.ForeignKey('card.id'))
	holo	= db.Column(db.Boolean)
	#num_normal=db.Column(db.Integer)
	#num_holo=db.Column(db.Integer)
