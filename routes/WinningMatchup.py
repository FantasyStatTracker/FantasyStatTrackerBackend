
from flask import Blueprint, request
from flask_cors import  cross_origin
import json
from Variables.TokenRefresh import oauth
from .FullData import getCategory

WinningMatchup_Blueprint = Blueprint('WinningMatchup', __name__)

@WinningMatchup_Blueprint.route('/category-leader', methods=['POST']) #Category Leaders
@cross_origin()
def getWins(*args):

    dataset = None
    try:
        dataset = args[0]
    except:
        pass

    if not oauth.token_is_valid():
        oauth.refresh_access_token()

    if (dataset == None):
        data = json.loads(request.form.get("data"))
    else:
        data = [json.loads(dataset)["TeamData"]]


    categoryArray = json.loads(getCategory().data)
    categoryMax = {category: {} for category in categoryArray}

    for teamStat in data:
        for team in list(teamStat.keys()):  # team stats
            for category in categoryArray:  # cats
                try:
                    categoryMax[category][team] = float(teamStat[team][category])
                except:
                    categoryMax[category][team] = 0.0
    
    return categoryMax


@WinningMatchup_Blueprint.route('/winning-matchups', methods=['POST']) #Team vs. Other Teams
@cross_origin()
def winning(*args):

    dataset = None
    try:
        dataset = args[0]
    except:
        pass
    if (dataset == None):
        data = json.loads(request.form.get("data"))
    else:
        data = [json.loads(dataset)["TeamData"]]

    currentWins = {}

    for allData in data:
        for player1 in list(allData.keys()):  # team stats
            currentWins[player1] = []
            for player2 in list(allData.keys()):

                if (player1 == player2):
                    continue

                winCount = 0
                catWins = []

                # different condition for Turnovers
                if (float(allData[player1]['TO']) < float(allData[player2]['TO'])):
                    winCount += 1
                    catWins.append('TO')
                for category in allData[player1].keys():  # cats

                    comparisonResult = float(allData[player1][category]) > float(allData[player2][category])
                    if (comparisonResult and (category != 'TO')):  # check how many wins
                        winCount += 1
                        catWins.append(category)

                if (winCount >= 5):
                    currentWins[player1].append({player2: catWins})

    return currentWins  # json object with Team { Wins { Categorieswon
