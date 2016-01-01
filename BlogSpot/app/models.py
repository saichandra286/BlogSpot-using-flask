import re
from app import db
from hashlib import md5
from app import app
from config import WHOOSH_ENABLED


import sys
if sys.version_info >= (3,0):
	enable_search = False
else:
	enable_search = WHOOSH_ENABLED
	if enable_search:
		import flask.ext.whooshalchemy as whooshalchemy


folwers = db.Table('folwers',
	db.Column('flowid', db.Integer, db.ForeignKey('user.id')),
	db.Column('flowedid', db.Integer, db.ForeignKey('user.id'))
	)

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	nickname = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(120), index=True, unique=True)
	posts = db.relationship('Post', backref='author', lazy='dynamic')
	about_me = db.Column(db.String(140))
	last_seen = db.Column(db.DateTime)
	folwd=db.relationship('User',
							secondary=folwers,
							primaryjoin=(folwers.c.flowid==id),
							secondaryjoin=(folwers.c.flowedid == id),
							backref=db.backref('folwers', lazy='dynamic'),
							lazy='dynamic')


	@staticmethod
	def makevalidname(nickname):
		return re.sub('[^a-zA-Z0-9_\.]', '', nickname)

	@staticmethod
	def makeuniqname(nickname):
		if User.query.filter_by(nickname=nickname).first() is None:
			return nickname
		version = 2
		while True:
			new_nickname = nickname + str(version)
			if User.query.filter_by(nickname=new_nickname).first() is None:
				break
			version += 1
		return new_nickname

	@property
	def is_authenticated(self):
		return True
	
	@property
	def is_active(self):
		return True
	
	@property
	def is_anonymous(self):
		return False

	def get_id(self):
		try:
			return unicode(self.id)
		except NameError:
			return str(self.id)

	def avatar(self, size):
		return 'http://www.gravatar.com/avatar/%s?d=mm&s=%d' % (md5(self.email.encode('utf-8')).hexdigest(), size)

	def folw(self, user):
		if not self.folwng(user):
			self.folwd.append(user)
			return self

	def unflow(self,user):
		if self.folwng(user):
			self.folwd.remove(user)
			return self

	def folwng(self,user):
		return self.folwd.filter(folwers.c.flowedid==user.id).count() > 0

	def folwed_post(self):
		return Post.query.join(folwers,(folwers.c.flowedid == Post.user_id)).filter(folwers.c.flowedid == self.id).order_by(Post.timestamp.desc())


	def __repr__(self):
		return '<User %r>' % (self.nickname)

class Post(db.Model):

	__searchable__ = ['body']


	id=db.Column(db.Integer, primary_key = True)
	body = db.Column(db.String(140))
	timestamp = db.Column(db.DateTime)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	langu = db.Column(db.String(5))

	def __repr__(self):
		return '<Post %r>' % (self.body)

if enable_search:
	whooshalchemy.whoosh_index(app, Post)
