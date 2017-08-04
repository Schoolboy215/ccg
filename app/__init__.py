# Import flask and template operators
from flask import Flask, render_template

# Import bootstrap
from flask_bootstrap import Bootstrap

# Import SQLAlchemy
from flask.ext.sqlalchemy import SQLAlchemy

# Import login system
from flask.ext.login import LoginManager, UserMixin, login_required

# Define the WSGI application object
app = Flask(__name__)

# Activate bootstrap
Bootstrap(app)

# Configurations
app.config.from_object('config')
app._static_folder = '/var/www/ccg/static'

# Create the login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.signin"

# Define the database object which is imported
# by modules and controllers
db = SQLAlchemy(app)

# Sample HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

# Import a module / component using its blueprint handler variable (mod_auth)
from app.mod_card.controllers import mod_card as card_module
from app.mod_auth.controllers import mod_auth as auth_module
from app.mod_profile.controllers import mod_profile as profile_module
from app.mod_trade.controllers import mod_trade as trade_module
from app.mod_main.controllers import mod_main as main_module


# Register blueprint(s)
app.register_blueprint(auth_module)
app.register_blueprint(card_module)
app.register_blueprint(profile_module)
app.register_blueprint(trade_module)
app.register_blueprint(main_module)
# app.register_blueprint(xyz_module)
# ..

# Build the database:
# This will create the database file using SQLAlchemy
db.create_all()

# Global methods
from app.mod_trade.models import TradeHeader, TradeLine
from flask.ext.login import LoginManager, UserMixin, login_required, login_user, current_user
def trade_count():
	if not hasattr(current_user,'id'):
		return "";
	trades = TradeHeader.query.filter((TradeHeader.user1_id == current_user.id) | (TradeHeader.user2_id == current_user.id),TradeHeader.active == True )
	if trades.count() > 0:
		return trades.count()
	else: 
		return "";

app.jinja_env.globals.update(trade_count = trade_count)

if __name__ == "__main__":
        app.run('0.0.0.0', debug=True)

