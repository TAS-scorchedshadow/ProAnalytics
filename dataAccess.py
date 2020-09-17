import sqlite3
from flask import g, session
from flask_login._compat import unicode

DATABASE = 'PARS.db'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3
        return db


# Adds a row to the users table of PARS.db with the indicated information
# Only used to add essential information
def addUser(username, fname, sname, school, email, password):
    conn = sqlite3.connect('PARS.db')
    c = conn.cursor()
    c.execute("INSERT INTO users (username, fName, sName, school, email, password)"
              "VALUES (?,?,?,?,?,?)",
              (username, fname, sname, school, email, password))
    conn.commit()
    conn.close()


def addShoot(shoot):
    # Adds a row to the 'shoots' table of PARS.db with shoot information,
    # Then adds all shots of that shoot to the 'shots' table of PARS.db
    conn = sqlite3.connect('PARS.db')
    c = conn.cursor()
    # Add data to shoots table
    c.execute("INSERT INTO shoots (username, rifleRange, distance, time, duration,"
              "groupSize, groupCentreX, groupCentreY,"
              "totalScore, totalShots, median, mean, std)"
              "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
              (shoot['username'], shoot['rifleRange'], shoot['distance'], shoot['time'], shoot['duration'],
               shoot['groupSize'], shoot['groupCentreX'], shoot['groupCentreY'],
               shoot['totalScore'], shoot['totalShots'],
               shoot['stats']['median'], shoot['stats']['mean'], shoot['stats']['std']))
    conn.commit()
    # Get ID of the added shoot
    c.execute('SELECT * FROM shoots ORDER BY shootID desc;')
    s = c.fetchone()
    shootID = s[0]
    shots = shoot['validShots']
    sighterCount = 0
    sighterList = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                   'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    # Add data to shots table
    for i in range(len(shots)):
        sighter = shots[i]['sighter']
        if sighter:
            shotNum = sighterList[sighterCount]
            sighterCount += 1
        else:
            shotNum = i + 1 - sighterCount
        c.execute("INSERT INTO shots (shootID, username, shotNum, sighter, score, scoreV, x, y, velocity)"
                  "VALUES (?,?,?,?,?,?,?,?,?)",
                  (shootID, shoot['username'], shotNum, sighter, shots[i]['score'], shots[i]['Vscore'],
                   shots[i]['x'], shots[i]['y'], shots[i]['v']))
    conn.commit()
    conn.close()


def usernameExists(username):  # Checks if username exists in database
    conn = sqlite3.connect('PARS.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username=?', (username,))
    result = c.fetchone()
    if result:
        return True
    else:
        return False


def findID(username):  # Checks if username exists in database
    conn = sqlite3.connect('PARS.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username=?', (username,))
    userid = c.fetchone()[0]
    return userid


def findPassword(username): #Finds an encrypted password in the database given a username
    conn = sqlite3.connect('PARS.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username=?', (username,))
    password = c.fetchone()[6]  # Gets position of password
    return password


def emailExists(email):  # Checks if email exists in database
    conn = sqlite3.connect('PARS.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE email=?', (email,))
    result = c.fetchone()
    if result:
        return True
    else:
        return False


def initialiseSettings(username):  # initialise user settings from database
    conn = sqlite3.connect('PARS.db')
    c = conn.cursor()
    for row in c.execute('SELECT * FROM users WHERE username=?', (username,)):
        print(row)
        session['fName'] = row[2]
        session['sName'] = row[3]
        session['school'] = row[4]
        session['email'] = row[5]
    conn.close()



