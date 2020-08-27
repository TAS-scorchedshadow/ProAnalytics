import sqlite3
from flask import g

DATABASE = 'PARS.db'


def get_db():
    db = getattr(g,'_database', None)
    if db is None:
        db = g._database = sqlite3
        return db


def addUser(username,fname,sname,school,email,password):
    conn = sqlite3.connect('PARS.db')
    c = conn.cursor()
    c.execute("INSERT INTO students (username, fName, sName, school, email, password) VALUES (?,?,?,?,?,?)",(username,fname,sname,school,email,password))
    conn.commit()
    conn.close()


def usernameExists(username): #Checks if username exists in database
    conn = sqlite3.connect('PARS.db')
    c = conn.cursor()
    c.execute('SELECT * FROM students WHERE username=?',(username,))
    result = c.fetchone()
    if result:
        return True
    else:
        return False


def emailExists(email): #Checks if email exists in database
    conn = sqlite3.connect('PARS.db')
    c = conn.cursor()
    c.execute('SELECT * FROM students WHERE email=?',(email,))
    result = c.fetchone()
    if result:
        return True
    else:
        return False



def query_db(query, args=(), one=False):
    cur = get_db().execute(query,args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv