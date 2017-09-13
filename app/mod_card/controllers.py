import random
import os
import json
# Import flask dependencies
from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for

from sqlalchemy import desc

# Import login manager
from flask.ext.login import LoginManager, UserMixin, login_required, login_user, current_user

# Import the database object from the main app module
from app import db
from app import app

# Import module forms
from app.mod_card.forms import CreateCardForm

# Import module models (i.e. User)
from app.mod_card.models import Card, UserCards
from app.mod_auth.models import User

# Define the blueprint: 'auth', set its url prefix: app.url/auth
mod_card = Blueprint('card', __name__, url_prefix='/card')

@mod_card.route('/<id>')
@login_required
def showCard(id):
	card = Card.query.filter_by(id=id).first()
	if not card:
		return "That ID doesn't exist", 400
	return render_template( "card/view.html",
				card=card,
				textBackground=app.config['TEXT_BACKGROUND'],
				borderColor=app.config['BORDER_COLOR'])

@mod_card.route('/index')
@mod_card.route('/', methods=['GET','POST'])
def indexCards():
	if request.method == 'GET':
		cards = Card.query.order_by(desc(Card.id)).all()
		return render_template(	"card/index.html",
					cards=cards,
					textBackground=app.config['TEXT_BACKGROUND'],
					borderColor=app.config['BORDER_COLOR'],
					cardsPerRow=app.config['CARDS_PER_ROW'])
	else:
		if request.form['searchTerm'] != '':
			cards = Card.query.filter(Card.name.like("%"+request.form['searchTerm']+"%")).order_by(desc(Card.id)).all()
		else:
			cards = Card.query.order_by(desc(Card.id)).all()
		toReturn = []
		for card in cards:
			toReturn.append([card.name,card.description,url_for('card.showCard', id=card.id), str(card.date_created)])
		return json.dumps(toReturn)

@mod_card.route('/<id>/edit', methods=['GET','POST'])
@login_required
def edit(id):
	card = Card.query.filter_by(id=id).first()
	if card:
		if request.method == 'GET':
			return render_template(	"card/edit.html",
						card=card)
		elif request.method == 'POST':
			card.name = request.form['name']
			card.description = request.form['description']
			card.backgroundColor = request.form['backgroundColor']
			card.holoAllowed = 'holoAllowed' in request.form
			card.holoAlways = 'holoAlways' in request.form
			db.session.commit()
			return redirect(url_for('card.showCard',id = card.id))
			return str(json.dumps(request.form)), 200
		
	else:
		return "That id doesn't exist", 400

@mod_card.route('/<id>/grant', methods=['POST'])
@login_required
def grantCard(id):
	card = Card.query.filter_by(id=id).first()
	if card:
		holo = False
		if (card.holoAllowed and random.randrange(app.config['HOLO_CHANCE']) == 0):
			holo = True
		if (card.holoAlways):
			holo = True			
		user_card = UserCards(card_id = card.id, user_id = current_user.id, holo = holo);
		db.session.add(user_card)
		db.session.commit()
	else:
		return "That id doesn't exist", 400
	return redirect(url_for('profiles.view',name = current_user.name))

@mod_card.route('/<id>/who', methods=['POST'])
@login_required
def who(id):
	card = Card.query.filter_by(id=id).first()
	if card:
		cards = UserCards.query.filter_by(card_id = card.id).group_by(UserCards.user_id)
		toReturn = []
		for i in cards:
			user = User.query.filter_by(id=i.user_id).first()
			count = user.cards.filter(UserCards.card_id == card.id).count()
			r = lambda: random.randint(0,255)
			color = '#{:02x}{:02x}{:02x}'.format(r(),r(),r())
			holo = UserCards.query.filter_by(user_id = i.user_id, card_id = i.card_id, holo = True).first()
			toReturn.append([user.name, (holo != None),count,color])
		return json.dumps(toReturn)
	else:
		return "That id doesn't exist", 400

@mod_card.route('/<id>/delete', methods=['POST'])
@login_required
def delete(id):
	card = Card.query.filter_by(id=id).first()
	if card:
		db.session.delete(card)
        	db.session.commit()
        	return redirect(url_for('card.indexCards'))	
	else:
		return "That isn't a valid id", 400

@mod_card.route('/create/', methods=['GET', 'POST'])
@login_required
def createCard():

	# If sign up form is submitted
	form = CreateCardForm(request.form)

	# Verify the sign up form
	if form.validate_on_submit():
		f = request.files['image']
		filename = ''.join(random.choice('0123456789ABCDEF') for i in range(10))
		f.save(os.path.join(
			app.config['UPLOAD_FOLDER'], filename+'.png'
		))
		card = Card(name=form.name.data,
			description = form.description.data,
			backgroundColor = form.backgroundColor.data,
			holoAlways = form.holoAlways.data,
			holoAllowed = form.holoAllowed.data,
			retired = False,
			imageName = filename
			)
		db.session.add(card)
	#	try:
		db.session.commit()
		card = Card.query.filter_by(imageName = filename).first()
		return redirect(url_for('card.showCard',id = card.id))
	#	except:
	#	flash('Error in creation', 'error')
	return render_template("card/create.html", form=form)
