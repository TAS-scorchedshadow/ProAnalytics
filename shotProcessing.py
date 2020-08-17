import math
import statistics
import json
def validateShots(filePath):
    numValidShot = 0
    newShot = {'id': 0, 'name':"",'validShots':[]}
    validShots = []
    with open(filePath) as json_file: #Open txt file as JSON
        data = json.load(json_file)
        for individualShot in data['shots']:
            x = individualShot['valid']
            if x:
                validShots.append(individualShot)
                numValidShot += 1

        if numValidShot != data["n_shots"]:         #Check to see if number of validated shots met expected value
            print("validateShots validated" , str(numValidShot), "shots. Which differed from the original JSON"
                  , str(data["n_shots"]))

        newShot['id'] = data['_id']
        newShot['name'] = data['name']
        newShot['validShots'] = validShots
    return newShot

def getScore(shot):
    score = {'score': 0, 'Vscore':0} #Vscore = 0 if none was given
    if shot['value'] == "V":                #JSON includes array if shot included a Vscore
        score['score'] = shot['score'][0]
        score['Vscore'] = shot['score'][1]
    else:
        score['score'] = shot['score']
    return score

#general calculations for the mean, median and range of the dataset. The information is returned at the bottom
#data brought in from the json, and the shot score statistical information is created
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
    return mean,median,scoreRange

if __name__ == "__main__":
    statisticsScore()