import sqlite3

from flask import Flask, request, jsonify
from flask.ext.cors import CORS
from datetime import datetime

db = sqlite3.connect('strikeout.db')
c = db.cursor()

app = Flask(__name__)
CORS(app)

@app.route('/')
def hello_world():
  print(dir(request))
  print(request.args.keys())
  print(request.args.values())

  return jsonify(**{'status': 'all good', 'time': 'today'})

@app.route('/register', methods=['POST'])
def register():
  """
  Given a username and a password, store information in the database, provided
  that the username isn't taken and the password meets requirements. 
  TODO: figure out hashing password.
  """

  def _check_username(username):
    """
    Determine whether username exists already. Return true iff it is available
    for use.
    """
    count = c.execute('''SELECT 
                           COUNT(*) as count
                         FROM
                           user
                         WHERE
                           username=?''', (username,)).fetchone()[0]

    print(count)
    return count == 0

  def _check_password(password):
    """
    Determine if password meets requirements. Return true iff it is valid.
    """
    return len(password) >= 6 and len(password) <= 64

  def _create_user(username, password):
    """
    Create user with given username and password. Return true iff the user was
    created.
    """
    try:
      c.execute('''INSERT INTO user VALUES (?, ?)''', (username, password))
    except sqlite3.OperationalError as e:
      return False

    return True

  if not _check_username(request.form['username']):
    return jsonify(error='Username taken')

  if not _check_password(request.form['password']):
    return jsonify(error='Password must be between 6 and 64 characters long')

  if not _create_user(request.form['username'], request.form['password']):
    return jsonify(error='Account not created')

  return jsonify(message='Account successfully created!')

@app.route('/create_trip', methods=['POST'])
def create_trip():
  """
  Given all necessary information about a trip: start time, start location,
  end location, driver username and the number of additional seats.

  Create a listing in the database for the trip.
  """

  data = request.form
  print(data)
  
  try:
    c.execute('''INSERT INTO trip (post_time, start_time, start_lat, start_lon,
                                   end_lat, end_lon, driver, additional_seats)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
              (datetime.now(),
               datetime.fromtimestamp(int(data['start_time'])/1000.0),
               float(data['start_lat']),
               float(data['start_lon']),
               float(data['end_lat']),
               float(data['end_lon']),
               data['driver'],
               int(data['additional_seats'])))
  except sqlite3.OperationalError as e:
    return jsonify(error='Trip not created')

  return jsonify(message='Trip successfully created')

@app.route('/show_all_trips', methods=['GET'])
def show_all_trips():
  """
  Show all future trips.
  TODO: Improve this function to sort trips by distance or filter out trips
  that are too far away.
  """

  all_trips = c.execute("""SELECT *
                           FROM
                             (SELECT *
                              FROM 
                                trip
                              WHERE
                                start_time < DATETIME('now')) a
                             LEFT OUTER JOIN
                             (SELECT 
                                tripid,
                                COUNT(*) as riders
                              FROM 
                                rider
                              WHERE 
                                request_approved IS NOT NULL) b
                             ON
                               a.tripid=b.tripid""").fetchall()

  trips = []
  for trip_tup in all_trips:
    trip = {}
    
    trip['tripid'] = trip_tup[0]
    trip['post_time'] = trip_tup[1]
    trip['start_time'] = trip_tup[2]
    trip['start_lat'] = trip_tup[3]
    trip['start_lon'] = trip_tup[4]
    trip['end_lat'] = trip_tup[5]
    trip['end_lon'] = trip_tup[6]
    trip['driver'] = trip_tup[7]
    trip['total_available_seats'] = trip_tup[8]
    trip['current_riders'] = trip_tup[10] or 0

    trips.append(trip)

  return jsonify(trips=trips)
    
def initialize_database():
  """
  Initialize database schema. Create all required tables. In the future, we
  might want to look into having this method restore state of database from
  backup file.
  """

  c.execute('''CREATE TABLE user (
                 username TEXT PRIMARY KEY,
                 password TEXT NOT NULL)''')

  c.execute('''CREATE TABLE trip (
                 tripid               INTEGER PRIMARY KEY,
                 post_time            DATE NOT NULL,
                 start_time           DATE NOT NULL,
                 start_lat            DECIMAL(9,3) NOT NULL,
                 start_lon            DECIMAL(9,3) NOT NULL,
                 end_lat              DECIMAL(9,3) NOT NULL,
                 end_lon              DECIMAL(9,3) NOT NULL,
                 driver               TEXT NOT NULL,
                 additional_seats     INTEGER NOT NULL,
                 FOREIGN KEY(driver) REFERENCES user(username))''')

  c.execute('''CREATE TABLE rider (
                 tripid               INTEGER PRIMARY KEY,
                 rider                TEXT NOT NULL,
                 request_sent         DATE NOT NULL,
                 request_approved     DATE,
                 FOREIGN KEY(rider) REFERENCES user(username))''')

  db.commit() 
                 
def main():
  initialize_database()
  app.run(debug=False, use_reloader=False)

if __name__ == '__main__':
  main()
