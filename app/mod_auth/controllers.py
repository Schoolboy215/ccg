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
from app.mod_auth.forms import LoginForm, SignupForm

# Import module models (i.e. User)
from app.mod_auth.models import User

# Define the blueprint: 'auth', set its url prefix: app.url/auth
mod_auth = Blueprint('auth', __name__, url_prefix='/auth')

import sys

# Set the route and accepted methods
@mod_auth.route('/signin/', methods=['GET', 'POST'])
def signin():

    # If sign in form is submitted
    form = LoginForm(request.form)

    # Verify the sign in form
    if form.validate_on_submit():

        user = User.query.filter_by(name=form.name.data).first()

        if user and check_password_hash(user.password, form.password.data):

            session['user_id'] = user.id

            login_user(user)

            return render_template('main/home.html')

        flash('Wrong email or password', 'error')
    return render_template("auth/signin.html", form=form)

@mod_auth.route('/signup/', methods=['GET', 'POST'])
def signup():

    # If sign up form is submitted
    form = SignupForm(request.form)

    # Verify the sign up form
    if form.validate_on_submit():

        user = User(name=form.name.data, password = form.password.data)
	db.session.add(user)
	try:
		db.session.commit()
		return redirect(url_for('profiles.view', name=user.name))
	except:
		flash('Username already taken', 'error')

    return render_template("auth/signup.html", form=form)

@mod_auth.route('/home')
@login_required
def home():
	return render_template('auth/home.html')
