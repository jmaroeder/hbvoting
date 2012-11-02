from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
		render_template, flash, _app_ctx_stack
from contextlib import closing
import csv


app = Flask(__name__)
app.config.from_pyfile('settings.py')



def connect_db():
	conn = sqlite3.connect(app.config['DATABASE'])
	conn.row_factory = sqlite3.Row
	conn.execute('pragma foreign_keys = on')
	return conn

def init_db():
	with closing(connect_db()) as db:
		with app.open_resource('schema.sql') as f:
			db.cursor().executescript(f.read())
		db.commit()
		
		
def load_db(csvfile):
	with closing(connect_db()) as db:
		with app.open_resource(csvfile) as f:
			rowreader = csv.DictReader(f)
			for row in rowreader:
				db.execute('INSERT INTO person (assigned_id, ethnicity, email, mentor, gender, city, party) VALUES (?, ?, ?, ?, ?, ?, ?)', 
						   [row['Assigned ID', row['Ethnicity:'], row['HB Email: (Must be @hb.edu)'], row['Mentor Group:'], row['Gender: '], row['City: '], row['Party Affiliation: ']])
		db.commit()

@app.before_request
def before_request():
	g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
	g.db.close()




@app.route('/')
def home():
	if not session.get('authorized'):
		abort(401)
	return render_template('home.html')


@app.route('/vote', methods=['POST'])
def vote():
	if not session.get('authorized'):
		abort(401)
	
	# verify valid voter id
	cur = g.db.execute('SELECT person.personid, person.assigned_id, vote.voteid FROM person LEFT JOIN vote ON person.personid = vote.personid WHERE assigned_id = ?', [request.form['voterid']]).fetchone()
	
	if cur:
		# check to make sure they haven't already voted
		row = cur.fetchone()
		if row['voteid'] == None:
			# we're good
			flash(request.form['choice'])
			g.db.execute('INSERT INTO vote (choice, personid) VALUES (?, ?)', [request.form['choice'], row['personid']])
			g.db.commit()
			flash('You voted for %s. <a href="%s">Click here to confirm.</a>' % (request.form['choice'], url_for('home')))
			return redirect(url_for('home'))
		else:
			flash("You've already voted!", category='error')
	else:
		flash('Invalid voter ID', category='error')
	
		
	return redirect(url_for('home'))

@app.route('/authorize', methods=['GET', 'POST'])
def authorize():
	error = None
	if request.method == 'POST':
		if request.form['code'] == app.config['AUTH_CODE']:
			session['authorized'] = True
			flash('Authorized')
			return redirect(url_for('home'))
		else:
			error = 'Invalid authorization code'
	return render_template('authorize.html', error=error)


if __name__ == '__main__':
	if not app.config['DEBUG']:
		app.run(host='0.0.0.0')
	else:
		app.run()
