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
class TradeHeader(Base):

	__tablename__ = 'trade_header'

	user1_id 	= db.Column(db.Integer, db.ForeignKey('user.id'))
	user2_id 	= db.Column(db.Integer, db.ForeignKey('user.id'))

	user1_approved 	= db.Column(db.Boolean)
	user2_approved 	= db.Column(db.Boolean)

	user1_seen 	= db.Column(db.Boolean)
	user2_seen 	= db.Column(db.Boolean)

	active		= db.Column(db.Boolean)

	lines		= db.relationship('TradeLine',
        		backref = 'trade', cascade='all, delete-orphan', lazy='dynamic')

	# New instance instantiation procedure
	def __init__(	self,
			user1,
			user2):

		self.user1_id		= user1.id
		self.user2_id		= user2.id
		self.user1_approved	= True
		self.user2_approved	= False
		self.user1_seen		= True
		self.user2_seen		= False
		self.active		= True
    

class TradeLine(Base):
	__tablename__ = 'trade_line'
	trade_id	= db.Column(db.Integer, db.ForeignKey('trade_header.id'))
	card_id		= db.Column(db.Integer, db.ForeignKey('user_cards.id'))
	offering_user	= db.Column(db.Integer, db.ForeignKey('user.id'))

	def __init__(	self,
			trade_id,
			card_id,
			offering_user):
		self.trade_id		= trade_id
		self.card_id		= card_id
		self.offering_user	= offering_user
