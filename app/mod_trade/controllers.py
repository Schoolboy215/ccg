import random
import os
import json
import datetime
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
from app.mod_trade.models import TradeHeader, TradeLine

# Define the blueprint: 'auth', set its url prefix: app.url/auth
mod_trade = Blueprint('trade', __name__, url_prefix='/trades')

def returnFullTrade(trade_id):
	toReturn = {}
	toReturn['lines'] = []
	line = {}
	trade = TradeHeader.query.filter_by(id=trade_id).first()
	for key, value in trade.__dict__.items():
		if type(value) is str or type(value) is int or type(value) is bool or type(value) is unicode or type(value) is datetime.datetime:
			toReturn[key] = value
		else:
			print(key + " " + str(type(value)))

	user = User.query.filter_by(id=trade.user1_id).first()
	toReturn['user1_name'] = user.name

	user = User.query.filter_by(id=trade.user2_id).first()
        toReturn['user2_name'] = user.name

	for trade_line in trade.lines:
		line = {}
		line['card'] = {}
		for key, value in trade_line.__dict__.items():
			if type(value) is str or type(value) is int or type(value) is bool or type(value) is unicode:
				line[key] = value
		user_card = UserCards.query.filter_by(id=trade_line.card_id).first()
		if not user_card:
			continue
		card = Card.query.filter_by(id=user_card.card_id).first()
		for key, value in card.__dict__.items():
			if type(value) is str or type(value) is int or type(value) is bool or type(value) is unicode:
				line['card'][key] = value
		line['holo'] = user_card.holo
		toReturn['lines'].append(line)

	if toReturn['user1_id'] == current_user.id:
		user = User.query.filter_by(id=toReturn['user2_id']).first()
		toReturn['otherUser_name'] = user.name
	else:
		user = User.query.filter_by(id=toReturn['user1_id']).first()
		toReturn['otherUser_name'] = user.name
			
	return toReturn

@mod_trade.route('/<id>/addCards', methods=['POST'])
@login_required
def addCards(id):
	trade = TradeHeader.query.filter_by(id=id).first()
	user = User.query.filter_by(id=current_user.id).first()
        if not trade:
                return "No such trade", 400
        if current_user.id != trade.user1_id and current_user.id != trade.user2_id:
                return "You are not involved in this trade", 400
	if not trade.active:
                return "This trade is complete", 400
	data = json.loads(request.form['checkedIds'])
	for card in data:
		if int(card['quantity']) < 1:
			continue
		tradeLine = TradeLine(trade_id = trade.id, card_id = card['id'], offering_user = current_user.id)
        	db.session.add(tradeLine)
        	db.session.commit()
		if int(card['quantity']) > 1:
			cardKind = user.cards.filter(UserCards.id == card['id']).first()
			usedIds = []
			for line in trade.lines.all():
				usedIds.append(line.card_id)
			for i in range(1,int(card['quantity'])):
				toRemove = user.cards.filter(UserCards.card_id == cardKind.card_id,~UserCards.id.in_(usedIds)).first()
				if not toRemove:
					continue
				tradeLine = TradeLine(trade_id = id, card_id = toRemove.id, offering_user = current_user.id)
				db.session.add(tradeLine)
				db.session.commit()
				usedIds.append(toRemove.id)
	trade.user2_approved = False
	trade.user1_approved = False
	db.session.commit()

	return "lines added", 200

@mod_trade.route('/<id>/removeCard', methods=['POST'])
@login_required
def removeCard(id):
	trade = TradeHeader.query.filter_by(id=id).first()
        if not trade:
                return "No such trade", 400
        if current_user.id != trade.user1_id and current_user.id != trade.user2_id:
                return "You are not involved in this trade", 400
	if not trade.active:
		return "This trade is complete", 400
	tradeLine = trade.lines.filter_by(card_id=int(request.form['cardId'])).first()
	db.session.delete(tradeLine)
        trade.user2_approved = False
        trade.user1_approved = False
        db.session.commit()
	return "line removed", 200

@mod_trade.route('/<id>/approve', methods=['POST'])
@login_required
def approve(id):
	trade = TradeHeader.query.filter_by(id=id).first()
	if not trade:
                return "No such trade", 400
        if current_user.id != trade.user1_id and current_user.id != trade.user2_id:
                return "You are not involved in this trade", 400
	if not trade.active:
                return "This trade is complete", 400

	if current_user.id == trade.user1_id:
		trade.user1_approved = True;
	else:
		trade.user2_approved = True;
	db.session.commit()
	if trade.user1_approved and trade.user2_approved:
		trade.active = False
		processTrade(id)
	return redirect(url_for('trade.showTrade', id=id))

def processTrade(id):
	trade = TradeHeader.query.filter_by(id=id).first()
	building = []
	for line in trade.lines.all():
		user = User.query.filter_by(id = line.offering_user).first()
		card = user.cards.filter_by(id = line.card_id).first()
		if not card:
			continue
		if line.offering_user == trade.user1_id:
			card.user_id = trade.user2_id
		else:
			card.user_id = trade.user1_id
	db.session.commit()	
	
@mod_trade.route('/<id>/myUnusedCards', methods=['POST'])
@login_required
def myUnusedCards(id):
	trade = TradeHeader.query.filter_by(id=id).first()
	if not trade:
		return "No such trade", 400
	if current_user.id != trade.user1_id and current_user.id != trade.user2_id:
                return "You are not involved in this trade", 400
	#fullTrade = returnFullTrade(id)
	usedIds = []
	for line in trade.lines.all():
		usedIds.append(line.card_id)
	print(usedIds)
	user = User.query.filter_by(id=current_user.id).first()
	toReturn = {}
	for userCard in user.cards.filter(~UserCards.id.in_(usedIds)).group_by(UserCards.card_id, UserCards.holo):
		#if userCard.id in usedIds:
		#	continue
		forInsert = {}
		cardRef = Card.query.filter_by(id=userCard.card_id).first()
		forInsert['cardName'] = cardRef.name
		forInsert['cardHolo'] = userCard.holo
		forInsert['quantity'] = user.cards.filter(~UserCards.id.in_(usedIds), UserCards.card_id == userCard.card_id, UserCards.holo == userCard.holo).count()
		toReturn[userCard.id] = forInsert
		#if card.holo:
		#	toReturn[card.id] +=" (holo)"
	return json.dumps(toReturn)
	

@mod_trade.route('/create', methods=['POST'])
@login_required
def create():
	otherUser = User.query.filter_by(id=request.args['otherUserId']).first()
	trade = TradeHeader(user1 = current_user, user2 = otherUser);
	db.session.add(trade)
	db.session.commit()

	tradeLine = TradeLine(trade_id = trade.id, card_id = request.args['cardId'], offering_user = otherUser.id)
	db.session.add(tradeLine)
	db.session.commit()

        return redirect(url_for('trade.showTrade',id = trade.id))
	#return str(otherUserId) + " " + str(current_user.id)

@mod_trade.route('/<id>')
@login_required
def showTrade(id):
	trade = TradeHeader.query.filter_by(id=id).first()
	if not trade:
		return "No such trade", 400
	if current_user.id != trade.user1_id and current_user.id != trade.user2_id:
		return "You are not involved in this trade", 400
	if not trade.active:
                return render_template('trade/complete.html')
	else:
		return render_template('trade/view.html', trade = returnFullTrade(trade.id))

@mod_trade.route('/')
@login_required
def index():
	trades = TradeHeader.query.filter((TradeHeader.user1_id == current_user.id) | (TradeHeader.user2_id == current_user.id),TradeHeader.active == True )
	tradeArray = []
	for trade in trades:
		tradeArray.append(returnFullTrade(trade.id))
	return render_template(	'trade/index.html',
				trades = tradeArray,
				user = current_user)
