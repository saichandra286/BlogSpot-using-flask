from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length

class LoginForm(Form):
	openid = StringField('openid', validators=[DataRequired()])
	remember_me = BooleanField('remember_me', default=False)

class EdF(Form):
	nickname = StringField('nickname', validators=[DataRequired()])
	about_me = TextAreaField('about_me', validators=[Length(min=0, max=140)])

	def __init__(self, original_nickname, *args, **kwargs):

		Form.__init__(self, *args, **kwargs)
		self.original_nickname = original_nickname

	def validate(self):
		if not Form.validate(self):
			return False
		if self.nickname.data == self.original_nickname:
			return True
		if self.nickname.data != User.makevalidname(self.nickname.data):
			self.nickname.errors.append(gettext('this nickname is invalid please u doted,letters,undersocure only'))
			return False
		user = User.query.filter_by(nickname=self.nickname.data).first()
		if user != None:
			self.nickname.errors.append('This nickname is already in use. Please choose another one.')
			return False
		return True

class postf(Form):
	post = StringField('post', validators=[DataRequired()])

class searchf(Form):
	search = StringField('search', validators = [DataRequired()])
