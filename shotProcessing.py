import math
import json
import numpy
from datetime import datetime


# All work in this file is done by Ryan T
# Reformats the shots to filter for relevant data
def validateShots(txtfile):
    totalShots = 0      # Total number of shots
    countingShots = 0   # Total, excluding sighters
    newShoot = {'id': 0, 'username': "", 'time': 0, 'duration': 0, 'validShots': [],
                'groupSize': 0.0, 'groupCentreX': 0.0, 'groupCentreY': 0.0}
    validShotList = []
    runningScore = {'score': 0, 'Vscore': 0}
    with open(txtfile) as json_file:  # Open txt file as JSON
        data = json.load(json_file)
        for individualShot in data['shots']:
            x = individualShot['valid']
            if x:
                score = getScore(individualShot)
                individualShot['score'] = score['score']
                individualShot['Vscore'] = score['Vscore']
                sighter = checkSighter(individualShot)
                individualShot['sighter'] = sighter
                validShotList.append(individualShot)
                totalShots += 1
                if not sighter:
                    countingShots += 1
                    runningScore['score'] += score['score']
                    runningScore['Vscore'] += score['Vscore']
        # Check to see if number of validated shots met expected value
        if totalShots != data["n_shots"]:
            print("validateShots validated: ", str(totalShots), "shots. Which differed from the original JSON"
                  , str(data["n_shots"]))
        # Send all the relevant data to a new dictionary, newShoot
        newShoot['id'] = data['_id']
        newShoot['username'] = data['name']
        firstShotTime = validShotList[0]['ts']              # time of last shot
        lastShotTime = validShotList[totalShots - 1]['ts']  # time of last shot
        newShoot['time'] = firstShotTime
        newShoot['dateTime'] = msToDatetime(firstShotTime)
        newShoot['duration'] = lastShotTime - firstShotTime
        newShoot['groupSize'] = data['stats_group_size']
        newShoot['groupCentreX'] = data['stats_group_center']['x']
        newShoot['groupCentreY'] = data['stats_group_center']['y']
        newShoot['validShots'] = validShotList
        newShoot['totalShots'] = countingShots
        newShoot['totalScore'] = str(runningScore['score']) + "." + str(runningScore['Vscore'])
        newShoot['stats'] = shotStats(validShotList)
        newShoot['shotList'] = shootList(validShotList)
    return newShoot


# Gets shot statistics
def shotStats(shoot):
    stats = {}
    shots = []
    for i in shoot:
        if not i['sighter']:
            shots.append(i['score'])
    stats['median'] = numpy.median(shots)
    stats['mean'] = numpy.mean(shots)
    stats['std'] = numpy.std(shots)
    return stats


def msToDatetime(ms):
    date = datetime.fromtimestamp(ms / 1000).strftime('%d/%m/%Y %H:%M')
    return date


# Gets shot statistics
def shootList(shoot):
    shots = []
    for i in shoot:
        shots.append(i['value'])
    return shots


# Reformats score into a dictionary of score and Vscore
def getScore(shot):
    score = {'score': 0, 'Vscore': 0}  # Vscore = 0 if none was given
    if shot['value'] == "V":                # JSON includes array if shot included a Vscore
        score['score'] = shot['score'][0]
        score['Vscore'] = shot['score'][1]
    else:
        score['score'] = shot['score']
    return score


# Checks if the shot is a sighter
def checkSighter(shot):
    try:
        return shot['sighter']
    except KeyError:
        return False


# Rishi's code. Have no idea what it does though
# Should not be necessary anymore, shotStats exists now. todo: Pending removal.

# general calculations for the mean, median, range & standard deviation of the dataset. The information is returned
# at the bottom data brought in from the json, and the shot score statistical information is created
def statisticsScore():
    jsonID = 1551500850141  # ID of json file
    filePath = "testJson/string-" + str(jsonID) + ".txt"
    s = validateShots(filePath)
    score = []
    totalShots = 0
    totalScore = 0
    for i in range(len(s['validShots'])):
        loopScore = getScore(s['validShots'][i])
        totalShots += 1
        totalScore = loopScore['score'] + totalScore
        score.append(loopScore["score"])
    score = sorted(score)
    mean = totalScore/totalShots
    if (len(score))%2 == 0:
        median = (((score[int(len(score)/2)])) + (((score[int(len(score)/2) + 1]))) ) / 2
    else:
        median = ((score[math.ceil(len(score)/2)]))
    scoreRange = score[-1] - score[0]
    stdDev = numpy.std(score)

    return mean, median, scoreRange, stdDev

if __name__ == "__main__":
    statisticsScore()