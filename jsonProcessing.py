
import json
def validateShots(txtfile):
    numValidShot = 0
    validShots = []
    with open(txtfile) as json_file:
        data = json.load(json_file)
        for individualShot in data['shots']:
            x = individualShot['valid']
            if x:
                validShots.append(individualShot)
                numValidShot += 1

        if numValidShot != data["n_shots"]:         #Check to see if number of validated shots met expected value
            print("validateShots validated" , str(numValidShot), "shots. Which differed from the original JSON"
                  , str(data["n_shots"]))
    return validShots