from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
		render_template, flash, _app_ctx_stack
from contextlib import closing


app = Flask(__name__)
app.config.from_pyfile('settings.py')



def connect_db():
	conn = sqlite3.connect(app.config['DATABASE'])
	conn.execute('pragma foreign_keys = on')
	return conn

def init_db():
	with closing(connect_db()) as db:
		with app.open_resource('schema.sql') as f:
			db.cursor().executeScript(f.read())
		db.commit()




@app.route('/')
def home():
	return render_template('home.html')


if __name__ == '__main__':
	if not app.config['DEBUG']:
		app.run(host='0.0.0.0')
	else:
		app.run()
