from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
		render_template, flash, _app_ctx_stack, Response
from contextlib import closing
import csv
import StringIO


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
						   [row['Assigned ID'], row['Ethnicity:'], row['HB Email: (Must be @hb.edu)'], row['Mentor Group:'], row['Gender: '], row['City: '], row['Party Affiliation: ']])
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
		return redirect(url_for('authorize'))
	return render_template('home.html')


@app.route('/vote', methods=['POST'])
def vote():
	if not session.get('authorized'):
		abort(401)
	
	# verify valid voter id
	row = g.db.execute('SELECT person.personid, person.assigned_id, vote.voteid FROM person LEFT JOIN vote ON person.personid = vote.personid WHERE assigned_id = ?', [request.form['voterid']]).fetchone()
	if row != None:
		# valid voter ID
		# check to make sure they haven't already voted
		if row['voteid'] == None:
			# haven't voted yet
			
			# check to make sure they made a choice
			if request.form.get('choice', None) != None and request.form['choice'] != '':
				g.db.execute('INSERT INTO vote (choice, personid) VALUES (?, ?)', [request.form['choice'], row['personid']])
				g.db.commit()
				flash('You voted for %s.' % (request.form['choice']))
				return redirect(url_for('confirm'))
			else:
				flash('You must choose a candidate.', category='error')
		else:
			flash("You've already voted!", category='error')
	else:
		flash('Invalid voter ID', category='error')
	
		
	return redirect(url_for('home'))

@app.route('/confirm')
def confirm():
	if not session.get('authorized'):
		abort(401)
	return render_template('confirm.html')


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


@app.route('/results.csv', methods=['GET', 'POST'])
def results():
	error = None
	if request.method == 'POST':
		if request.form['code'] == app.config['AUTH_CODE']:
			# build and return results CSV
			cur = g.db.execute('SELECT person.ethnicity, person.mentor, person.gender, person.city, person.party, vote.choice FROM person LEFT JOIN vote ON person.personid = vote.personid')
			rows = cur.fetchall()
			
			output = StringIO.StringIO()
			writer = csv.DictWriter(output, rows[0].keys(), extrasaction='ignore')
			writer.writeheader()
			
			for row in rows:
				tRow = {}
				for k in row.keys():
					tRow[k] = row[k]
			
				writer.writerow(tRow)
			
			return Response(output.getvalue(), mimetype='text/csv')
			
			# TODO
		else:
			error = 'Invalid authorization code'
	return render_template('results.html', error=error)


if __name__ == '__main__':
	if not app.config['DEBUG']:
		app.run(host='0.0.0.0')
	else:
		app.run()
