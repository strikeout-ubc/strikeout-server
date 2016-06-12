import sqlite3

from flask import Flask

db = sqlite3.connect('strikeout.db')
c = db.cursor()

app = Flask(__name__)

@app.route('/')
def hello_world():
  return 'Hello World'

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
                 start_time           DATE NOT NULL,
                 start_lat            DECIMAL(9,3) NOT NULL,
                 start_lon            DECIMAL(9,3) NOT NULL,
                 end_lat              DECIMAL(9,3) NOT NULL,
                 end_lon              DECIMAL(9,3) NOT NULL,
                 driver               TEXT NOT NULL,
                 additional_seats     INTEGER NOT NULL,
                 FOREIGN KEY(driver) REFERENCES user(username))''')

  c.execute('''CREATE TABLE riders (
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
