from flask.ext.mail import Message
from app import mail
from flask import render_template
from config import ADMINS
from app import app
from threading import Thread
from .decorators import async

@async
def sendAsynMail(app,msg):
	with app.app_context():
		mail.send(msg)


def send_email(subj, sender, reci, txtbody, htmlbody):
	msg = Message(subj, sender=sender, recipients=reci)
	msg.body = txtbody
	msg.html = htmlbody
	sendAsynMail(app, msg)

def folwrnoti(folwd, folwr):
	send_email("[microblog] %s is now following u" % folwr.nickname,
				ADMINS[0],
				[folwd.email],
				render_template("folwr_mail.txt",
								user=folwd, folwr=folwr),
				render_template("folwr_mail.html",
								user=folwd, folwr=folwr))
