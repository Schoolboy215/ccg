# Import Form and RecaptchaField (optional)
from flask.ext.wtf import Form # , RecaptchaField
from flask.ext.wtf.file import FileField, FileRequired

# Import Form elements such as TextField and BooleanField (optional)
from wtforms import TextField, PasswordField, TextAreaField, RadioField, BooleanField

# Import Form validators
from wtforms.validators import Required, Email, EqualTo


# Define the login form (WTForms)

class CreateCardForm(Form):
	name    = TextField('name')
	description = TextAreaField('description')
	holoAllowed = BooleanField(label='Holographic allowed')
	holoAlways = BooleanField(label = 'Holographic always')
	image = FileField()
	backgroundColor = TextField('color')
	
