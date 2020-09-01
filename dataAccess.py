import sqlite3
from flask import g, session

DATABASE = 'PARS.db'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3
        return db


def addUser(username, fname, sname, school, email, password): #Adds a row to the users table of PARS.db with the indicated information
    conn = sqlite3.connect('PARS.db')
    c = conn.cursor()
    c.execute("INSERT INTO users (username, fName, sName, school, email, password) VALUES (?,?,?,?,?,?)",
              (username, fname, sname, school, email, password))
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


def findPassword(username): #Finds an encrypted password in the database given a username
    conn = sqlite3.connect('PARS.db')
    c = conn.cursor()
    for row in c.execute('SELECT * FROM users WHERE username=?', (username,)):
        password = row[6]  # Gets position of password
    conn.close()
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
        if row[8] == 1:  # If user is an admin
            session['type'] = 'admin'
        else:
            session['type'] = 'student'
        session['rifleSerial'] = row[7]
    conn.close()


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv
