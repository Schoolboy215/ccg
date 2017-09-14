import random
import os
import json
import re
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
#from app.mod_card.forms import CreateCardForm

# Import module models (i.e. User)
from app.mod_card.models import Card, UserCards
from app.mod_auth.models import User
from app.mod_trade.models import TradeHeader

# Define the blueprint: 'auth', set its url prefix: app.url/auth
mod_profile = Blueprint('profiles', __name__, url_prefix='/profiles')

@mod_profile.route('/')
def index():
	users = User.query.all()
	return render_template( "profile/index.html", users = users)

@mod_profile.route('/<name>')
@login_required
def view(name):
	user = User.query.filter(User.name.like(name)).first()
	#if user.id == current_user.id:
	#	trades = TradeHeader.query.filter((TradeHeader.user1_id == current_user.id) | (TradeHeader.user2_id == current_user.id))
	#	return "This is you"
	return redirect(url_for('profiles.cardIndex',name=name))

@mod_profile.route('/<name>/cards')
@login_required
def cardIndex(name):
	user = User.query.filter(User.name.like(name)).first()
	if not user:
		return "No such user", 404
	cardLookup = user.cards.order_by(desc(UserCards.date_modified)).group_by(UserCards.card_id, UserCards.holo)
	cards = []
	holoList = []
	quantities = []
	for i in cardLookup:
		card = Card.query.filter_by(id=i.card_id).first()
		count = user.cards.filter(UserCards.card_id == card.id, UserCards.holo == i.holo).count()
		quantities.append(count)
		cards.append(card)
		holoList.append(i.holo)
	return render_template(	"profile/view.html",
				user = user,
				cards = cards,
				cardLookup = cardLookup,
				holoList=holoList,
				quantities=quantities,
				textBackground = app.config['TEXT_BACKGROUND'],
                                borderColor=app.config['BORDER_COLOR'],
                                cardsPerRow=app.config['CARDS_PER_ROW'])

@mod_profile.route('/<name>/card/<id>')
@login_required
def cardKind(name,id):
	user = User.query.filter(User.name.like(name)).first()
	if not user:
		return "No such user", 404
	holo = request.args.get('holo') == "True"
	cards = user.cards.filter(UserCards.card_id == id, UserCards.holo == holo).order_by(desc(UserCards.id)).all()
	if not cards:
		return "That user doesn't have any of that card", 404
	card = Card.query.filter_by(id=cards[0].card_id).first()
	cardLookup = card
	return render_template( "profile/kind.html",
                                user = user,
				cards = cards,
                                card = card,
                                cardLookup = card,
                                holo = holo,
                                textBackground = app.config['TEXT_BACKGROUND'],
                                borderColor = app.config['BORDER_COLOR'])		

@mod_profile.route('/<name>/cards/<id>')
@login_required
def viewUserCard(name,id):
        user = User.query.filter(User.name.like(name)).first()
        if not user:
                return "no such user", 400
        card = user.cards.filter_by(id=id).first()
        if not card:
                return "no such card for that user", 400
	
        cardType = Card.query.filter_by(id=card.card_id).first()
        holo = card.holo
        if current_user.id == user.id:
                ownedCard = True
        else:
                ownedCard = False
	cardHistory = []
	id = re.escape(id)
	result = db.engine.execute('SELECT * FROM trade_line JOIN trade_header ON trade_header.id = trade_line.trade_id AND trade_line.card_id = '+id+' JOIN	user u1 ON u1.id = trade_header.user1_id JOIN user u2 ON u2.id = trade_header.user2_id ORDER BY trade_line.id desc;')
	for row in result:
		offering = row[5]
		givingName = ''
		gettingName = ''
		user1 = row[9]
		user2 = row[10]
		if offering == user1:
			givingName = row[19]
			gettingName = row[24]
		else:
			givingName = row[24]
			gettingName = row[19]
		cardHistory.append({'giving':givingName,'getting':gettingName,'date': row[1][0:10]})
	origin = {}
	origin['puller'] = user.name
	origin['date'] = str(card.date_created)[0:10]
	if len(cardHistory):
		origin['puller'] = cardHistory[len(cardHistory)-1]['giving']
        return render_template( "profile/card.html",
                                user = user,
                                card = cardType,
                                cardLookup = card,
                                holo = holo,
                                ownedCard = ownedCard,
				cardHistory = cardHistory,
				origin = origin,
				justPulled = False,
                                textBackground = app.config['TEXT_BACKGROUND'],
                                borderColor = app.config['BORDER_COLOR'])

@mod_profile.route('/<name>/cards/<cardId>/delete', methods=['POST'])
@login_required
def deleteCard(name,cardId):
	user = User.query.filter(User.name.like(name)).first()
	if user.id is not current_user.id:
		return "please don't try that again", 400
        if not user:
                return "no such user", 400
	card = user.cards.filter_by(id=cardId).first()
        if not card:
                return "no such card for that user", 400
	db.session.delete(card)
	db.session.commit()
	return redirect(url_for('profiles.view', name=user.name))
