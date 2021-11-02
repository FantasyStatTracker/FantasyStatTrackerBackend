
from flask import Blueprint, request
from flask_cors import  cross_origin
import json
from Variables.TokenRefresh import oauth, lg
from .FullData import getCategory, test

WinningMatchup_Blueprint = Blueprint('WinningMatchup', __name__)

from Model.variable import MatchupHistory, db

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

    print(type(data))
    currentWins = {}

    for x in data:
        print(x)
        for player1 in list(x.keys()):  # team stats
            currentWins[player1] = []
            for y in data:
                for player2 in list(y.keys()):

                    if (player1 == player2):
                        continue

                    winCount = 0
                    catWins = []

                    # different condition for Turnovers
                    if (float(x[player1]['TO']) < float(y[player2]['TO'])):
                        winCount += 1
                        catWins.append('TO')
                    for z in x[player1].keys():  # cats

                        comp = float(x[player1][z]) > float(y[player2][z])
                        if (comp and z != 'TO'):  # check how many wins
                            winCount += 1
                            catWins.append(z)

                    if (winCount >= 5):
                        currentWins[player1].append({player2: catWins})

    return currentWins  # json object with Team { Wins { Categorieswon


@WinningMatchup_Blueprint.route('/updatePreviousWeek', methods=['GET']) #winning 
@cross_origin()
def te():

    previousWeek = lg.current_week()-2

    previousWeekData = test(previousWeek).get_data()
    
    previousWinningMatchups = winning(previousWeekData).get_data().decode('utf-8')
    previousLeaders = getWins(previousWeekData).get_data().decode('utf-8')
    previousWeekData = previousWeekData.decode('utf-8')
    previousWeekData = json.loads(previousWeekData)["TeamData"]

    matchupRecord = MatchupHistory(
        matchup_week=previousWeek, 
        all_data=json.dumps(previousWeekData), 
        winning_matchup=previousWinningMatchups, 
        leader=previousLeaders
    )
    db.session.add(matchupRecord)
    db.session.commit()
    
    return "Update Complete"