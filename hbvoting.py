from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
		render_template, flash, _app_ctx_stack


app = Flask(__name__)
app.config.from_pyfile('settings.py')



def connect_db():
	return sqlite3.connect(app.config['DATABASE'])





@app.route('/')
def home():
	return render_template('home.html')


if __name__ == '__main__':
	if not app.config['DEBUG']:
		app.run(host='0.0.0.0')
	else:
		app.run()
