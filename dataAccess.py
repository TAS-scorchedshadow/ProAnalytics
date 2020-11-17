import sqlite3
import numpy
from datetime import datetime
import graphProcessing
from flask import g, session
from flask_login._compat import unicode
import psycopg2
DB_NAME = "dwjfhvlj"
DB_USER = "dwjfhvlj"
DB_PASS = "8thg6lLwJuI00TJrJqd7bUAax05gNZDF"
DB_HOST = "topsy.db.elephantsql.com"
DB_PORT = "5432"

DATABASE = 'PARS.db'

# todo: Rewrite ALL database functions to use %s instead of ? (see addShoot(shoot) )


def connect():
    conn = psycopg2.connect(database=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST, port=DB_PORT)
    return conn


# -- Henry Guo --
# capitalise first letter in string
def capitalise(string):
    return string[0].upper() + string[1:]


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3
        return db


# -- Henry Guo --
# convert to unix time (ts)
# date is a string in the format dd/mm/yyyy
def convertTimeStr(date):
    newDate = time.mktime(datetime.strptime(date, "%d-%m-%y").timetuple()) * 1000
    return newDate


# -- Henry Guo --
# convert unix time into readable string (dd/mm/yyyy)
# ts is unix time in milliseconds as an integer
def convertStrTime(ts):
    newDate = datetime.fromtimestamp(int(ts) / 1000).strftime('%d-%m-%y')
    return newDate


# -- Ryan Tan --
# Adds a row to the 'shoots' table of database with shoot information,
# Then adds all shots of that shoot to the 'shots' table of the database
def addShoot(shoot):
    conn = connect()
    c = conn.cursor()
    # Add data to shoots table
    SQL = """
          INSERT INTO shoots (username, rifleRange, distance, time, duration,
          groupSize, groupCentreX, groupCentreY,
          totalScore, totalShots, median, mean, std, weather)
          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
          """
    data = (shoot['username'], shoot['rifleRange'], shoot['distance'], shoot['time'], shoot['duration'],
            shoot['groupSize'], shoot['groupCentreX'], shoot['groupCentreY'],
            shoot['totalScore'], shoot['totalShots'],
            shoot['stats']['median'], shoot['stats']['mean'], shoot['stats']['std'], shoot['weather'])
    c.execute(SQL, data)
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
        SQL = """
              INSERT INTO shots (shootID, username, shotNum, sighter, score, scoreV, x, y, velocity, datetime)
              VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
              """
        data = (shootID, shoot['username'], shotNum, str(sighter), shots[i]['score'], str(shots[i]['Vscore']),
                shots[i]['x'], shots[i]['y'], shots[i]['v'], shots[i]['ts'])
        c.execute(SQL, data)
    conn.commit()
    conn.close()


# -- Following by Dylan Huynh --
# Adds a row to the users table of PARS.db with the indicated information
# Only used to add essential information
def addUser(username, fname, sname, school, email, password,year):
    conn = connect()
    c = conn.cursor()
    SQL = """
          INSERT INTO users (username, fName, sName, school, email, password, year)
          VALUES (%s, %s, %s, %s, %s, %s, %s)
          """
    data = (username, fname, sname, school, email, password, year)
    c.execute(SQL, data)
    conn.commit()
    conn.close()


# Checks if username exists in database
def usernameExists(username):
    conn = connect()
    c = conn.cursor()
    SQL = "SELECT * FROM users WHERE username=%s"
    data = (username,)
    c.execute(SQL, data)
    result = c.fetchone()
    if result:
        return True
    else:
        return False


# Checks if username exists in database
def findID(username):
    conn = connect()
    c = conn.cursor()
    SQL = "SELECT * FROM users WHERE username=%s"
    data = (username,)
    c.execute(SQL, data)
    userid = c.fetchone()[0]
    return userid


# Finds an encrypted password in the database given a username
def findPassword(username):
    conn = connect()
    c = conn.cursor()
    SQL = "SELECT * FROM users WHERE username=%s"
    data = (username,)
    c.execute(SQL, data)
    password = c.fetchone()[6]  # Gets position of password
    return password


def emailExists(email):  # Checks if email exists in database
    conn = connect()
    c = conn.cursor()
    SQL = "SELECT * FROM users WHERE email=%s"
    data = (email,)
    c.execute(SQL, data)
    result = c.fetchone()
    if result:
        return True
    else:
        return False


# initialise user settings from database
def initialiseSettings(username):
    conn = connect()
    c = conn.cursor()
    SQL = "SELECT * FROM users WHERE username=%s"
    data = (username,)
    for row in c.execute(SQL, data):
        print(row)
        session['fName'] = row[2]
        session['sName'] = row[3]
        session['school'] = row[4]
        session['email'] = row[5]
    conn.close()
# -- End of Dylan's functions --


# -- Rishi Wig --  < Unused >
# creates a list of tuples of all ranges possible
def shoot_range():
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT distance FROM shoots")
    rows = c.fetchall()
    all = []
    for row in rows:
        create_tuple = (row[0], row[0])
        all.append(create_tuple)
    return all


# -- Henry Guo -- < Unused >
# creates a list of all of the shooter's names in the users table
def get_all_shooter_names():
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT fName, sName, admin FROM users")
    names = c.fetchall()
    shooters = []
    for name in names:
        if name[2] == 0:
            addName = capitalise(name[0]) + " " + capitalise(name[1])
            if addName not in shooters:
                shooters.append(addName)
    print(addName)
    return shooters


# -- Henry Guo --
# creates a list of all of the usernames in the shoots table
def get_all_usernames():
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT username FROM users")
    names = c.fetchall()
    usernames = []
    for name in names:
        if name[0] not in usernames:
            usernames.append(name[0])
    return usernames


# -- Rishi Wig  and Henry Guo --
# collect all the dates that a shooter has shot in and returns it as a list (sorted from latest to oldest)
def get_all_dates(shooter):
    conn = connect()
    c = conn.cursor()
    SQL = "SELECT time FROM shoots WHERE username=%s ORDER BY time desc;"
    data = (shooter,)
    c.execute(SQL, data)
    shootTimes = c.fetchall()
    timeList = []
    for shoot in shootTimes:
        stringDate = datetime.fromtimestamp(int(shoot[0]) / 1000).strftime('%d-%m-%y')
        if (stringDate, stringDate) not in timeList:
            create_tuple = (stringDate, stringDate)
            timeList.append(create_tuple)
    print(timeList)
    return timeList


# -- Rishi Wig--
# get a tuple of lists that contain all the information on a shoot from a shooter in a specific time frame
def get_shoots(shooter, dayStart, dayEnd):
    conn = connect()
    c = conn.cursor()
    SQL = "SELECT * FROM shoots WHERE username=%s AND time BETWEEN %s AND %s ORDER BY time desc;"
    data = (shooter, dayStart, dayEnd)
    c.execute(SQL, data)
    shoots = c.fetchall()
    print(shoots)
    return shoots


# -- Rishi Wig --
def get_graph_details(username, distance, time):
    conn = connect()
    c = conn.cursor()
    SQL = """
          SELECT groupSize, groupCentreX, groupCentreY, totalScore, shootID, median, mean, std, weather, totalShots
          FROM shoots WHERE username=%s AND distance=%s AND time=%s;
          """
    data = (username, distance, time)
    c.execute(SQL, data)
    shoots = c.fetchall()
    return shoots


# -- Rishi Wig --
def get_shot_details(shootID):
    conn = connect()
    c = conn.cursor()
    SQL = "SELECT shotNum, x, y, score FROM shots WHERE shootID=%s"
    data = (shootID,)
    c.execute(SQL, data)
    shoots = c.fetchall()
    return shoots


# -- Henry Guo --
# return a list of dictionaries which contain all the information on a shoot, including a target's script div
def get_shoots_dict(shooter, dayStart, dayEnd):
    conn = connect()
    c = conn.cursor()
    shot_table = {}
    target_list = []

    shoots = get_shoots(shooter, dayStart, dayEnd)
    # search through each shoot to collect a list of shots
    for shoot in shoots:
        shot_table[str(shoot[0])] = []
        SQL = "SELECT * FROM shots WHERE shootID=%s"
        data = (shoot[0],)
        c.execute(SQL, data)
        range = shoot[3]
        shots_tuple = c.fetchall()
        shots = {}
        duration = str(int((shoot[4]) / 60000)) + ' mins ' + str(int((shoot[4]) / 1000) % 60) + ' secs'
        for row in shots_tuple:
            shots[row[9]] = [row[5], row[3], row[6]]
            # create list of shots
            shot_table[str(shoot[0])].append((row[6], row[9]))
            # row[9] is shotNum
            # row[5] is x
            # row[3] is y
            # row[6] is score
        # create graph and put the data into target_list (along with shotNum)
        script, div = graphProcessing.drawTarget(shots, range, (shoot[6] / 2), (shoot[7], shoot[8]))
        date = datetime.fromtimestamp(int(shoot[1]) / 1000).strftime("%H:%M (%d/%m/%Y)")
        standard_dev = round(shoot[13], 2)
        mean = round(shoot[12], 1)
        target_list.append(
            {
                'id': (str(shoot[0])),
                'target_script': script,
                'target_div': div,
                'date': date,
                'total_score': shoot[9],
                'group_size': round(shoot[6] / 2, 2),
                'duration': duration,
                'mean': mean,
                'sd': standard_dev,
                'distance': shoot[3],
            }
        )
    return target_list, shot_table


# -- Henry Guo --
# return a dictionary containing the average score out of 50 and sd for each range
def get_table_stats(shooter):
    conn = connect()
    c = conn.cursor()
    SQL = "SELECT * FROM shoots WHERE username=%s ORDER BY time desc;"
    data = (shooter,)
    c.execute(SQL, data)
    shoots = c.fetchall()
    num_of_shots = 0
    quick_table = {}
    for shoot in shoots:
        # average score (changed to out of 50)
        avgScore = (float(shoot[9]) / (int(shoot[10]) * 5)) * 50
        sd = float(shoot[13])
        if shoot[3] not in quick_table:
            quick_table[shoot[3]] = {'avgScore': [avgScore],
                                     'sd': [sd],
                                     }
        else:
            quick_table[shoot[3]]['avgScore'].append(avgScore)
            quick_table[shoot[3]]['sd'].append(sd)
        num_of_shots += shoot[10]
    for distance in quick_table:
        print(quick_table[distance]['avgScore'])
        quick_table[distance]['avgScore'] = round(numpy.mean(quick_table[distance]['avgScore']), 1)
        quick_table[distance]['sd'] = round(numpy.mean(quick_table[distance]['sd']), 2)

    # sort the quick_table list so that the rows on the table are in ascending order (from top to bottom)
    # https://www.geeksforgeeks.org/python-convert-dictionary-to-list-of-tuples/
    sorted_table = [(k, v) for k, v in quick_table.items()]
    sorted_table = sorted(sorted_table, key=lambda t: t[0])
    print(sorted_table)
    stages_shot = len(shoots)
    stat_dict = {'sorted_table': sorted_table, 'num_of_shots': num_of_shots, 'stages_shot': stages_shot}
    return stat_dict


# -- Henry Guo --
# create the script and div for a line graph that compares the scores for each range over time
def get_line_graph_ranges(shooter):
    conn = connect()
    c = conn.cursor()
    # create line graph
    SQL = "SELECT * FROM shoots WHERE username=%s ORDER BY time asc;"
    data = (shooter,)
    c.execute(SQL, data)
    shoots = c.fetchall()
    values = {}
    lineList = []  # should end up looking like [ [300m, [x,x,x,x,x], [y,y,y,y,y]] , [500m, [x,x,x,x,x], [y,y,y,y,y]] ]
    listx = []
    listy = []
    listName = []
    for shoot in shoots:
        distance = shoot[3]
        avgScore = (float(shoot[9])/(int(shoot[10])*5))*50
        dateOfShoot = datetime.fromtimestamp(int(shoot[1]) / 1000).strftime('%d/%m/%Y')
        isInList = False
        for data in lineList:
            if distance in data:
                data[1].append(avgScore)
                data[2].append(dateOfShoot)
                isInList = True
        if not isInList:
            lineList.append([distance, [avgScore, ], [dateOfShoot, ]])

    # sort the lineList from lowest range to highest range
    lineList = sorted(lineList, key=lambda x: x[0])
    # convert lineList into a format (a dictionary) that the line graph function understands
    for dist in lineList:
        values[dist[0]] = {
            'xValue': dist[2],
            'yValue': dist[1]
        }
    # for data in lineList:
    #     listName.append(data[0])
    #     listx.append(data[1])
    #     listy.append(data[2])
    line_script, line_div = graphProcessing.compareLine(values, 'Dates', 'Scores (Out of 50)', 'Scores for Each Range')
    return line_script, line_div


# -- Henry Guo --
# collect the dates for every shooter in a dictionary and separated by range
def get_dates_for_all():
    all_dates = {}
    conn = connect()
    c = conn.cursor()
    c.execute('SELECT username FROM users')
    users = c.fetchall()
    for user in users:
        dateDict = {}
        SQL = "SELECT distance, time FROM shoots WHERE username=%s ORDER BY time desc;"
        data = (user[0],)
        c.execute(SQL, data)
        shoots = c.fetchall()
        for shoot in shoots:
            date = datetime.fromtimestamp(int(shoot[1]) / 1000).strftime('%d/%m/%Y (%H:%M)')
            if shoot[0] not in dateDict:
                dateDict[shoot[0]] = [(date, shoot[1])]
            else:
                dateDict[shoot[0]].append((date, shoot[1]))
        all_dates[user[0]] = dateDict
    return all_dates


# -- Henry Guo --
# collect the ranges every shooter has in a dictionary
def get_ranges_for_all():
    all_ranges = {}
    conn = connect()
    c = conn.cursor()
    c.execute('SELECT username FROM users')
    users = c.fetchall()
    for user in users:
        all_ranges[user[0]] = []
        SQL = "SELECT distance FROM shoots WHERE username=?;"
        data = (user[0])
        c.execute(SQL, data)
        shoots = c.fetchall()
        for shoot in shoots:
            if shoot[0] not in all_ranges[user[0]]:
                all_ranges[user[0]].append(shoot[0])
    return all_ranges


# -- Henry Guo --
# collect shooter and their year group they are in into a dictionary
def get_shooter_and_year():
    all_shooters = {}
    conn = connect()
    c = conn.cursor()
    c.execute('SELECT username, fName, sName, year FROM users WHERE admin IS 0 ORDER BY year asc')
    users = c.fetchall()
    for user in users:
        if user[3] not in all_shooters:
            all_shooters[user[3]] = [[user[0], capitalise(user[1]), capitalise(user[2])]]
        else:
            print(all_shooters)
            all_shooters[user[3]].append([user[0], capitalise(user[1]), capitalise(user[2])])
    print(all_shooters)
    return all_shooters
