# Author: Rohan Mirchandani
# Date: October 11, 2016
# Contact: mirchandani.rohan@gmail.com

from flask import Flask, request, g, jsonify
import sqlite3
import os
from datetime import datetime, date
import calendar
from collections import defaultdict

# setup the server configs
app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
	DATABASE = os.path.join(app.root_path, 'tanda.db'),
	SECRET_KEY='secret123',
	USERNAME='admin',
	PASSWORD='password'
	))
app.config.from_envvar('SETTINGS', silent = True)

# create connect to the database from the server
def connect_db():
	rv = sqlite3.connect(app.config['DATABASE'])
	return rv

# create global handle for database access for the server
def get_db():
	if ~hasattr(g, 'sqlite_db'):
		g.sqlite_db = connect_db()
	return g.sqlite_db

# initalize the database
def init_db():
	db = get_db()
	with app.open_resource('schema.sql', mode='r') as f:
		db.cursor().executescript(f.read())
	db.commit()

# call to initialize the database from commandline to enable data pesistance
@app.cli.command('initdb')
def initdb_command():
	init_db()
	print ('Database initialized.')

# handle POST requests and store data in the sqlite database
@app.route('/<deviceID>/<time>', methods=['POST'])
def ping(deviceID, time):
	db = get_db()
	db.execute('INSERT INTO pings (device_id, epoch_time) VALUES (?, ?)', [deviceID, time])
	db.commit()
	print("Data stored.")
	return ''

@app.route('/<deviceID>/<date>', methods=['GET'])
def retrieve_date(deviceID, date):
	# establish handle to database
	db = get_db()

	# datetime formatting
	startTime = datetime.strptime(date, '%Y-%m-%d')
	startEpoch = calendar.timegm(startTime.utctimetuple())
	endEpoch = startEpoch + 86400

	# allow for all data of all device_id's from a single day to be queried, as well as a specified device
	if deviceID == 'all':
		cursor = db.execute('SELECT * FROM pings WHERE epoch_time BETWEEN ? AND ?', [deviceID, startEpoch, endEpoch - 1])
	else:
		cursor = db.execute('SELECT epoch_time FROM pings WHERE device_id=? AND epoch_time BETWEEN ? AND ?', [deviceID, startEpoch, endEpoch - 1])

	# return list of query results
	data = cursor.fetchall()
	print("Data retrieved")

	# return JSON formatted list of query
	return jsonify(data)

# route to handle GET requests for data from the server between two times
@app.route('/<deviceID>/<rawStart>/<rawEnd>', methods=['GET'])
def retrieve_date2date(deviceID, rawStart, rawEnd):
	db = get_db()

	# handle time values based on format to allow for flexibilty of requests
	if rawStart.isdigit():
		startEpoch = float(rawStart)
	else:
		rawStart = datetime.strptime(rawStart, '%Y-%m-%d')
		startEpoch = calendar.timegm(rawStart.utctimetuple())

	if rawEnd.isdigit():
		endEpoch = float(rawEnd)
	else:
		rawEnd = datetime.strptime(rawEnd, '%Y-%m-%d')
		endEpoch = calendar.timegm(rawEnd.utctimetuple())

	# allow for GET requests for eithe ALL device data, or a specified device between two points in time
	if deviceID == 'all':
		cursor = db.execute('SELECT * FROM pings WHERE epoch_time BETWEEN ? AND ?', [startEpoch, endEpoch])
		data = cursor.fetchall()

		# create dictionary (hash) with the data from the query
		allDict = defaultdict(list);
		for i, j in data:
			allDict[i].append(j)

		print("Data retrieved")

		# return the hash in a JSON format
		return jsonify(allDict)

	else:
		cursor = db.execute('SELECT epoch_time FROM pings WHERE device_id=? AND epoch_time BETWEEN ? AND ?', [deviceID, startEpoch, endEpoch - 1])
		data = cursor.fetchall()
		print("Data retrieved")
		return jsonify(data)
	
# clear database when POST requested to /clear_data
@app.route('/clear_data', methods=['POST'])
def clear_data():
	db = get_db()
	db.execute('DELETE FROM pings')
	db.commit()
	print("Data cleared.")
	return ''

# return list of device_id's when GET requested to /devices
@app.route('/devices', methods=['GET'])
def get_devices():
	db = get_db()
	cursor = db.execute('SELECT DISTINCT device_ID FROM pings')
	data = cursor.fetchall()
	return jsonify(data)
