
import json
def validateShots(txtfile):
    numValidShot = 0
    newShot = {'id': 0, 'name':"",'validShots':[]}
    validShots = []
    with open(txtfile) as json_file: #Open txt file as JSON
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
