from flask import Blueprint, render_template, jsonify
import yahoo_fantasy_api as yfa
from yahoo_oauth import OAuth2
from collections import OrderedDict
from Variables.CurrentPrediction import Prediction
from Variables.Schedule2021 import *
from flask_cors import CORS, cross_origin
from Variables.TeamPlayer import WeeklyStat
from Variables.LeagueInformation import *
from Variables.TokenRefresh import token


data = token()

oauth = data["oauth"]
gm = data["gm"]
lg = data["lg"]

Prediction = Blueprint('Prediction', __name__)
cors = CORS(Prediction)
def getMatchups(): #predict

    matchupInfo = lg.matchups()
    teams = OrderedDict()
    data = matchupInfo["fantasy_content"]["league"][1]["scoreboard"]["0"]["matchups"]
    matchupKey = list(data.keys())
    matchupKey = matchupKey[:-1]

    P1 = ""
    Matchup = {}
    current = ""
    for matchupIndex in matchupKey:
        # matchup will always have two people
        for matchupIndividualTeam in range(0, 2):
            for index, TeamData in enumerate(data[matchupIndex]["matchup"]["0"]["teams"][str(matchupIndividualTeam)]["team"]):

                try:

                    if (matchupIndividualTeam == 0):
                        P1 = TeamData[0]['team_key']
                    else:
                        Matchup[P1] = TeamData[0]['team_key']
                except:
                    continue

    return Matchup


@Prediction.route('/fix', methods=['GET']) #fix data
def fix():
    Fix = WeeklyStat

    for team in Fix:
        for player in Fix[team]:
            player[0]["team"] = player[1]
            del(player[1])

    return Fix


@Prediction.route('/prediction-fast', methods=['GET']) #prediction
def predictionFast():
    return jsonify(Prediction)


@Prediction.route('/predict', methods=['GET']) #prediction
def predict():
    if not oauth.token_is_valid():
        oauth.refresh_access_token()
    count = 0
    weekRange = (lg.week_date_range(lg.current_week()))

    a = {"PTS": 0.0, "FG%": 0.0, "AST": 0.0, "FT%": 0.0,
         "3PTM": 0.0, "ST": 0.0, "BLK": 0.0, "TO": 0.0, "REB": 0.0}

    L = []
    Schedule = []
    teams = lg.teams()

    GameCounter = {}
    StatPrediction = {}
    for x in Sched["April"].keys():
        if (str(weekRange[0]) <= x <= str(weekRange[1])):
            L.append(x)
            for z in Sched["April"][x]:
                Schedule.append(z[0])
                Schedule.append(z[1])

    for x in Schedule:
        if (x in GameCounter):
            GameCounter[x] += 1

        else:
            GameCounter[x] = 1

    matchupInfo = lg.matchups(lg.current_week()-1)

    data = matchupInfo["fantasy_content"]["league"][1]["scoreboard"]["0"]["matchups"]

    FGFT = getFGFT()

    for team in teams:
        a = {"PTS": 0.0, "FG%": 0.0, "AST": 0.0, "FT%": 0.0,
             "3PTM": 0.0, "ST": 0.0, "BLK": 0.0, "TO": 0.0, "REB": 0.0}

        for player in WeeklyStat[team]:

            if (player[0]["team"].upper() in GameCounter.keys()):

                gamePlayer = GameCounter[player[0]["team"].upper()]
                for x in a.keys():
                    try:
                        a[x] += player[0][x]
                    except:
                        continue

            try:
                a["FG%"] = float(FGFT[team][0])
                a["FT%"] = float(FGFT[team][1])
            except:
                if (team == "402.l.67232.t.2"):
                    a["FG%"] = 0.5085836909871244
                    a["FT%"] = 0.6791044776119403
                elif (team == "402.l.67232.t.4"):
                    a["FG%"] = 0.4581673306772908
                    a["FT%"] = 0.8629032258064516

                elif (team == "402.l.67232.t.5"):
                    a["FG%"] = 0.48747591522157996
                    a["FT%"] = 0.8518518518518519
                elif (team == "402.l.67232.t.7"):
                    a["FG%"] = 0.44288577154308617
                    a["FT%"] = 0.8415841584158416
                pass

        StatPrediction[team] = a

    matchUp = getMatchups()

    h = matchUp

    cats = len(statMap)
    PredictionArray = []

    for team in h:
        opponent = h[team]
        Prediction = {team: 0, opponent: 0}
        for cat1 in StatPrediction[team]:
            if (cat1 == 'TO'):
                if (StatPrediction[team][cat1] < StatPrediction[opponent][cat1]):
                    Prediction[team] += 1
                elif (StatPrediction[team][cat1] > StatPrediction[opponent][cat1]):
                    Prediction[opponent] += 1
                else:
                    continue
                continue

            if (StatPrediction[team][cat1] > StatPrediction[opponent][cat1]):
                Prediction[team] += 1
            elif (StatPrediction[team][cat1] < StatPrediction[opponent][cat1]):
                Prediction[opponent] += 1
            else:
                continue

        PredictionArray.append(Prediction)

    for x in StatPrediction:
        StatPrediction[x]['FG%'] = round(StatPrediction[x]['FG%'], 3)
        StatPrediction[x]['FT%'] = round(StatPrediction[x]['FT%'], 3)

    ReturnPrediction = []

    for x in PredictionArray:
        newDict = {}
        for h in x.keys():
            newDict[TeamMap[h]] = [x[h], StatPrediction[h]]
        ReturnPrediction.append(newDict)

    return jsonify(ReturnPrediction)


@Prediction.route('/FG', methods=['GET']) #data
def getFGFT():

    matchupInfo = lg.matchups(lg.current_week()-1)
    teams = OrderedDict()
    data = matchupInfo["fantasy_content"]["league"][1]["scoreboard"]["0"]["matchups"]
    matchupKey = list(data.keys())
    matchupKey = matchupKey[:-1]

    teamFGFT = {}
    current = ""
    tempVar = ""
    for matchupIndex in matchupKey:
        # matchup will always have two people
        for matchupIndividualTeam in range(0, 2):
            for TeamData in data[matchupIndex]["matchup"]["0"]["teams"][str(matchupIndividualTeam)]["team"]:
                try:

                    tempVar = TeamData[0]['team_key']
                except:
                    try:
                        teamFGFT[tempVar] = [
                            convert_to_float(
                                TeamData["team_stats"]["stats"][0]['stat']['value']),
                            convert_to_float(
                                TeamData["team_stats"]["stats"][2]['stat']['value'])
                        ]

                    except:
                        continue

    return teamFGFT