from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.babel import gettext
from app import app, db, lm, oid, babel
from .forms import LoginForm, EdF, postf, searchf
from .models import User, Post
from datetime import datetime
from config import POSTS_PER_PAGE, lang
from .email import folwrnoti
from guess_language import guessLanguage
from flask import jsonify
from .translate import microsoft_translate

@lm.user_loader
def load_user(id):
	return User.query.get(int(id))


@babel.localeselector
def get_locale():
	return 'es'     #request.accept_languages.best_match(lang.keys())

@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
	if g.user is not None and g.user.is_authenticated:
		return redirect(url_for('index'))
	form = LoginForm()
	if form.validate_on_submit():
		session['remember_me'] = form.remember_me.data
		return oid.try_login(form.openid.data, ask_for=['nickname', 'email'])
		flash('Login requested for openid="%s", remember_me= %s' %(form.openid.data, str(form.remember_me.data)))
		return redirect('/index')
	return render_template('login.html',
							title='Sign In',
							form=form,
							providers=app.config['OPENID_PROVIDERS'])

@app.before_request
def before_request():
	g.user = current_user
	if g.user.is_authenticated:
		g.user.last_seen = datetime.utcnow()
		db.session.add(g.user)
		db.session.commit()
		g.searchFrm = searchf()
	g.locale = get_locale()


@app.errorhandler(404)
def not_found_error(error):
	return render_template('404.html'), 404

@app.errorhandler(505)
def internal_error(error):
	db.session.rollback()
	return render_template('505,html'), 505

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/index/<int:page>', methods=['GET', 'POST'])
@login_required
def index(page=1):
	form = postf()
	if form.validate_on_submit():
		language = guessLanguage(form.post.data)
		if language == 'UNKNOWN' or len(language)>5:
			language = ''
		post = Post(body=form.post.data, timestamp=datetime.utcnow(), author=g.user)
		db.session.add(post)
		db.session.commit()
		flash('successfuly posted ur post')
		return redirect(url_for('index'))
	posts = g.user.folwd.paginate(page, POSTS_PER_PAGE, False).items
	return render_template('index.html',
                           	title='Home',
                           	user=user,
                           	form=form,
                           	posts=posts)

@oid.after_login
def after_login(resp):
	if resp.email is None or resp.email == "":
		flash(gettext('Invalid Login'))
		return redirect(url_for('login'))
	user=User.query.filter_by(email=resp.email).first()
	if user is None:
		nickname = resp.nickname
		if nickname is None or nickname =="":
			nickname = resp.email.split('@')[0]
		nickname = User.makevalidname(nickname)
		nickname = User.makeuniqname(nickname)
		user = User(nickname=nickname, email=resp.email)
		db.session.add(user)
		db.session.commit()
		db.session.add(user.folw(user))
		db.session.commit();
	remember_me = False
	if 'remember_me' in session:
		remember_me = session['remember_me']
		session.pop('remember_me', None)
	login_user(user, remember = remember_me)
	return redirect(request.args.get('next') or url_for('index'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/user/<nickname>')
@app.route('/user/<nickname>/<int:page>')
@login_required
def user(nickname, page=1):
	user=User.query.filter_by(nickname=nickname).first()
	if user == None:
		flash('User %s not found.' %nickname)
		return redirect(url_for('index'))
	posts = user.posts.paginate(page, POSTS_PER_PAGE, False)
	return render_template('user.html',
							user=user,
							posts=posts)

@app.route('/edt', methods=['GET', 'Post'])
@login_required
def edt():
	form = EdF(g.user.nickname)
	if form.validate_on_submit():
		g.user.nickname = form.nickname.data
		g.user.about_me = form.about_me.data
		db.session.add(g.user)
		db.session.commit()
		flash('saves successfuly')
		return redirect(url_for('edt'))
	else:
		form.nickname.data = g.user.nickname
		form.about_me.data = g.user.about_me
	return render_template('edt.html', form=form)

@app.route('/folw/<nickname>')
@login_required
def follow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User %s not found.' % nickname)
        return redirect(url_for('index'))
    if user == g.user:
        flash('You can\'t follow yourself!')
        return redirect(url_for('user', nickname=nickname))
    u = g.user.folw(user)
    if u is None:
        flash('Cannot follow ' + nickname + '.')
        return redirect(url_for('user', nickname=nickname))
    db.session.add(u)
    db.session.commit()
    flash('You are now following ' + nickname + '!')
    folwrnoti(user, g.user)
    return redirect(url_for('user', nickname=nickname))

@app.route('/unflow/<nickname>')
@login_required
def unfollow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User %s not found.' % nickname)
        return redirect(url_for('index'))
    if user == g.user:
        flash('You can\'t unfollow yourself!')
        return redirect(url_for('user', nickname=nickname))
    u = g.user.unflow(user)
    if u is None:
        flash('Cannot unfollow ' + nickname + '.')
        return redirect(url_for('user', nickname=nickname))
    db.session.add(u)
    db.session.commit()
    flash('You have stopped following ' + nickname + '.')
    return redirect(url_for('user', nickname=nickname))

@app.route('/search', methods=['POST'])
@login_required
def search():
	if not g.searchFrm.validate_on_submit():
		return redirect(url_for('index'))
	return redirect(url_for('searchres', query=g.searchFrm.search.data))

@app.route('/searchres/<query>')
@login_required
def searchres(query):
	Sres = Post.query.all()
	return render_template('searchres.html',
							query=query,
							Sres = Sres)


@app.route('/translate', methods=['POST'])
@login_required
def translate():
    return jsonify({ 
        'text': microsoft_translate(
            request.form['text'], 
            request.form['sourceLang'], 
            request.form['destLang']) })

@app.route('/delete/<int:id>')
@login_required
def delete(id):
	post = Post.query.get(id)
	if post is None:
		flash('Post not found.')
		return redirect(url_for('index'))
	if post.author.id!=g.user.id:
		flash('you cannot delete this post.')
		return redirect(url_for('index'))
	db.session.delete(post)
	db.session.commit()
	flash('your post has been deleted.')
	return redirect(url_for('index'))
