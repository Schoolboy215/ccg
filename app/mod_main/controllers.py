# Import flask dependencies
from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for

# Import password / encryption helper tools
from werkzeug import check_password_hash, generate_password_hash

# Import login manager
from flask.ext.login import LoginManager, UserMixin, login_required, login_user

# Import the database object from the main app module
from app import db

# Import module forms
#from app.mod_auth.forms import LoginForm, SignupForm

# Import module models (i.e. User)
from app.mod_auth.models import User

# Define the blueprint: 'auth', set its url prefix: app.url/auth
mod_main = Blueprint('main', __name__, url_prefix='/')

# Set the route and accepted methods
@mod_main.route('/', methods=['GET'])
def home():
	return render_template('main/home.html')
