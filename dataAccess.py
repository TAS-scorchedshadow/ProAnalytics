import sqlite3
import numpy
from datetime import datetime
import graphProcessing
from flask import g, session
from flask_login._compat import unicode

DATABASE = 'PARS.db'


# capitalise first letter in string
def capitalise(string):
    return string[0].upper() + string[1:]


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
    # addShoot done by Ryan T
    # Adds a row to the 'shoots' table of PARS.db with shoot information,
    # Then adds all shots of that shoot to the 'shots' table of PARS.db
    conn = sqlite3.connect('PARS.db')
    c = conn.cursor()
    # Add data to shoots table
    c.execute("INSERT INTO shoots (username, rifleRange, distance, time, duration,"
              "groupSize, groupCentreX, groupCentreY,"
              "totalScore, totalShots, median, mean, std, weather)"
              "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
              (shoot['username'], shoot['rifleRange'], shoot['distance'], shoot['time'], shoot['duration'],
               shoot['groupSize'], shoot['groupCentreX'], shoot['groupCentreY'],
               shoot['totalScore'], shoot['totalShots'],
               shoot['stats']['median'], shoot['stats']['mean'], shoot['stats']['std'], shoot['weather']))
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
        c.execute("INSERT INTO shots (shootID, username, shotNum, sighter, score, scoreV, x, y, velocity, datetime)"
                  "VALUES (?,?,?,?,?,?,?,?,?,?)",
                  (shootID, shoot['username'], shotNum, sighter, shots[i]['score'], shots[i]['Vscore'],
                   shots[i]['x'], shots[i]['y'], shots[i]['v'], shots[i]['ts']))
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

def shoot_range(): #creates a list of tuples of all ranges possible
    conn = sqlite3.connect('PARS.db')
    cur = conn.cursor()
    cur.execute("SELECT distance FROM shoots")
    rows = cur.fetchall()
    all = []
    for row in rows:
        create_tuple = (row[0], row[0])
        all.append(create_tuple)
    return all

def get_all_shooter_names(): #creates a list of all of the shooter's names in the users table
    conn = sqlite3.connect("PARS.db")
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

def get_all_usernames(): #creates a list of all of the usernames in the shoots table
    conn = sqlite3.connect("PARS.db")
    c = conn.cursor()
    c.execute("SELECT username FROM users")
    names = c.fetchall()
    usernames = []
    for name in names:
        if name[0] not in usernames:
            usernames.append(name[0])
    return usernames

def get_all_dates(shooter):  # collect all the dates that a shooter has shot in and returns it as a list (sorted from latest to oldest)
    conn = sqlite3.connect("PARS.db")
    c = conn.cursor()
    c.execute('SELECT time FROM shoots WHERE username=? ORDER BY time desc;', (shooter,))
    shootTimes = c.fetchall()
    timeList = []
    for shoot in shootTimes:
        stringDate = datetime.fromtimestamp(int(shoot[0]) / 1000).strftime('%d-%m-%y')
        if (stringDate, stringDate) not in timeList:
            create_tuple = (stringDate, stringDate)
            timeList.append(create_tuple)
    print(timeList)
    return timeList

def get_shoots(shooter, dayStart, dayEnd):  # get a tuple of lists that contain all the information on a shoot from a shooter in a specific time frame
    conn = sqlite3.connect("PARS.db")
    c = conn.cursor()
    c.execute('SELECT * FROM shoots WHERE username=? AND time BETWEEN ? AND ? ORDER BY time desc;',
              (shooter, dayStart, dayEnd))
    shoots = c.fetchall()
    print(shoots)
    return shoots

def get_graph_details(username,distance, time):
    conn = sqlite3.connect("PARS.db")
    c = conn.cursor()
    c.execute('SELECT groupSize,groupCentreX,groupCentreY,totalScore, shootID, median, mean, std, weather FROM shoots WHERE username=? AND distance=? AND time=?;',
              (username, distance, time))
    shoots = c.fetchall()
    return shoots

def get_shot_details(shootId):
    conn = sqlite3.connect("PARS.db")
    c = conn.cursor()
    c.execute('SELECT shotNum, x, y, score FROM shots WHERE shootID=?;', (shootId,))
    shoots = c.fetchall()
    return shoots


def get_shoots_dict(shooter, dayStart, dayEnd):  # return a list of dictionaries which contain all the information on a shoot, including a target's script div
    conn = sqlite3.connect("PARS.db")
    c = conn.cursor()
    shot_table = {}
    target_list = []

    shoots = get_shoots(shooter, dayStart, dayEnd)
    # search through each shoot to collect a list of shots
    for shoot in shoots:
        shot_table[str(shoot[0])] = []
        c.execute('SELECT * FROM shots WHERE shootID=?', (shoot[0],))
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
        date = datetime.fromtimestamp(int(shoot[1]) / 1000).strftime('%d-%m-%y')
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


def get_table_stats(shooter):  # return a dictionary containing the average percentage score and sd for each range
    conn = sqlite3.connect("PARS.db")
    c = conn.cursor()
    c.execute('SELECT * FROM shoots WHERE username=? ORDER BY time desc;', (shooter,))
    shoots = c.fetchall()
    num_of_shots = 0
    quick_table = {}
    for shoot in shoots:
        if shoot[3] not in quick_table:
            quick_table[shoot[3]] = {'percentage': list([(float(shoot[9]) / (int(shoot[10]) * 5)) * 100]),
                                     'sd': list([float(shoot[13])])}
        else:
            quick_table[shoot[3]]['percentage'].append((float(shoot[9]) / (int(shoot[10]) * 5)) * 100)
            quick_table[shoot[3]]['sd'].append(float(shoot[13]))
        num_of_shots += shoot[10]
    for distance in quick_table:
        quick_table[distance]['percentage'] = round(numpy.mean(quick_table[distance]['percentage']), 1)
        quick_table[distance]['sd'] = round(numpy.mean(quick_table[distance]['sd']), 2)

    # sort the quick_table list so that the rows on the table are in ascending order (from top to bottom)
    # https://www.geeksforgeeks.org/python-convert-dictionary-to-list-of-tuples/
    sorted_table = [(k, v) for k, v in quick_table.items()]
    sorted_table = sorted(sorted_table, key=lambda t: t[0])
    print(sorted_table)
    stages_shot = len(shoots)
    stat_dict = {'sorted_table': sorted_table, 'num_of_shots': num_of_shots, 'stages_shot': stages_shot}
    return stat_dict


def get_line_graph_ranges(shooter):  # create the script and div for a line graph that compares the scores for each range over time
    conn = sqlite3.connect("PARS.db")
    c = conn.cursor()
    # create line graph
    c.execute('SELECT * FROM shoots WHERE username=? ORDER BY time asc;', (shooter,))
    shoots = c.fetchall()
    values = {}
    lineList = []  # should end up looking like [ [300m, [x,x,x,x,x], [y,y,y,y,y]] , [500m, [x,x,x,x,x], [y,y,y,y,y]] ]
    listx = []
    listy = []
    listName = []
    for shoot in shoots:
        distance = shoot[3]
        percentageScore = (float(shoot[9])/(int(shoot[10])*5))*100
        dateOfShoot = datetime.fromtimestamp(int(shoot[1]) / 1000).strftime('%d/%m/%Y')
        isInList = False
        for data in lineList:
            if distance in data:
                data[1].append(percentageScore)
                data[2].append(dateOfShoot)
                isInList = True
        if not isInList:
            lineList.append([distance, [percentageScore, ], [dateOfShoot, ]])

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
    line_script, line_div = graphProcessing.compareLine(values, 'Dates', 'Scores', 'Scores for Each Range')
    return line_script, line_div


def get_dates_for_all():  # collect the dates for every shooter in a dictionary and separated by range
    all_dates = {}
    conn = sqlite3.connect("PARS.db")
    c = conn.cursor()
    c.execute('SELECT username FROM users')
    users = c.fetchall()
    for user in users:
        dateDict = {}
        c.execute('SELECT distance, time FROM shoots WHERE username=?;', (user[0],))
        shoots = c.fetchall()
        for shoot in shoots:
            date = datetime.fromtimestamp(int(shoot[1]) / 1000).strftime('%d/%m/%Y')
            if shoot[0] not in dateDict:
                dateDict[shoot[0]] = [(date, shoot[1])]
            else:
                dateDict[shoot[0]].append((date, shoot[1]))
        all_dates[user[0]] = dateDict
    return all_dates


def get_ranges_for_all():  # collect the ranges every shooter has in a dictionary
    all_ranges = {}
    conn = sqlite3.connect("PARS.db")
    c = conn.cursor()
    c.execute('SELECT username FROM users')
    users = c.fetchall()
    for user in users:
        all_ranges[user[0]] = []
        c.execute('SELECT distance FROM shoots WHERE username=?;', (user[0],))
        shoots = c.fetchall()
        for shoot in shoots:
            if shoot[0] not in all_ranges[user[0]]:
                all_ranges[user[0]].append(shoot[0])
    return all_ranges


def get_shooter_and_year():  # collect shooter and their year group they are in into a dictionary
    all_shooters = {}
    conn = sqlite3.connect("PARS.db")
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
