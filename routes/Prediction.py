from flask import Blueprint, render_template, jsonify, request
import yahoo_fantasy_api as yfa
from yahoo_oauth import OAuth2
from collections import OrderedDict
from Variables.CurrentPrediction import Prediction
from Variables.Schedule2021 import *
from flask_cors import CORS, cross_origin
from Variables.WeeklyStats import WeeklyStat
from Variables.TeamPlayer import Q
from Variables.LeagueInformation import TeamMap, statMap
from Variables.TokenRefresh import oauth, gm, lg, apiKey
from Variables.CurrentMatchup import WeekMatchup as currentWeekMatchup
from routes.RelevantData import getTeamMap
from Variables.TeamMap import *
import os, time, stat
import json




Prediction_Blueprint = Blueprint('Prediction', __name__)
cors = CORS(Prediction_Blueprint)

@Prediction_Blueprint.route('/fix', methods=['GET']) #fix data, not needed anymore
def fix():
    Fix = WeeklyStat

    for team in Fix:
        for player in Fix[team]:

            
            player[0]["team"] = player[1]
            del(player[1])

    return Fix


@Prediction_Blueprint.route('/prediction-fast', methods=['GET']) #prediction
def predictionFast():
    return jsonify(Prediction)


@Prediction_Blueprint.route('/predict', methods=['GET']) #prediction
def predict():
    
    headers = request.headers
    auth = headers.get("X-Api-Key")

    if (auth == apiKey):
        if not oauth.token_is_valid():
            oauth.refresh_access_token()
        count = 0

        weekRange = (lg.week_date_range(lg.current_week()))


        teams = lg.teams()

        StatPrediction = {}
        '''
        L = []
        Schedule = []
        GameCounter = {}
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
        '''

        matchupInfo = lg.matchups(lg.current_week()-1)
        data = matchupInfo["fantasy_content"]["league"][1]["scoreboard"]["0"]["matchups"]
        FGFT = getFGFT()

        for team in teams:
            a = {"PTS": 0.0, "FG%": 0.0, "AST": 0.0, "FT%": 0.0,
                "3PTM": 0.0, "ST": 0.0, "BLK": 0.0, "TO": 0.0, "REB": 0.0}

            for player in WeeklyStat[team]:

                for x in a.keys():
                    try:
                        a[x] += player[0][x]
                    except:
                        continue

                try:
                    a["FG%"] = float(FGFT[team][0])
                    a["FT%"] = float(FGFT[team][1])
                except:
                    continue
                '''
                except:
                    #only for this week
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
                '''

            StatPrediction[team] = a

        matchUp = currentWeekMatchup

        
        PredictionArray = []

        for team in matchUp:
            opponent = matchUp[team]
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
            for match in x.keys():
                newDict[TeamMap[match]] = [x[match], StatPrediction[match]]
            ReturnPrediction.append(newDict)

    else:
        return jsonify({"message":"ERROR: unauthorized"}), 401

    with open('./Variables/Prediction.py', 'w') as fo:
        fo.write("Prediction =" + json.dumps(jsonify(ReturnPrediction)))
        fo.close
    return jsonify(ReturnPrediction)


#Returns Team FG% and FT% for the week
@Prediction_Blueprint.route('/FG', methods=['GET']) #data
def getFGFT():

    headers = request.headers
    auth = headers.get("X-Api-Key")

    if (auth == apiKey):
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
    else:
        return jsonify({"message":"ERROR: unauthorized"}), 401

    return teamFGFT

#returns top performers per team by category lead
@Prediction_Blueprint.route('/TopPerformers', methods=['POST'])
def getTopPerformers():

    data = json.loads(request.form.get("team"))
    TeamToFetch = ""

    if (data not in TeamMap.values()): #update team mapping iff there was a change (10x faster)
        newTeamMap = getTeamMap()

        with open('./Variables/TeamMap.py', 'w') as fo:
            fo.write("TeamMap =" + json.dumps(newTeamMap))

    
    for x in TeamMap:
        if (TeamMap[x] == data):
            TeamToFetch = x
            break

    PlayerList = Q
    MaxCat = {}
    catKeys = {}
    
    for category in PlayerList[TeamToFetch]:
        catKeys = category.keys()
    
    MaxCat = dict.fromkeys(catKeys, {"Value": 0.0, "PlayerFirst": "", "PlayerLast": ""})
    for category in PlayerList[TeamToFetch]:
        
        for individualCategory in category:
        
            
            if (isinstance(category[individualCategory], float)):
                
                
                if (MaxCat[individualCategory]["Value"] <= float(category[individualCategory])):
                    Name = category["name"].split()
                        
                    MaxCat[individualCategory] = {"Value": float(category[individualCategory]), 
                                                      "PlayerFirst": Name[0],
                                                      "PlayerLast": Name[1]
                                                 }



    delete = []
    for key in MaxCat:
        if (MaxCat[key]["PlayerFirst"] == ""):
            delete.append(key)


    for deletionKey in delete:
        del MaxCat[deletionKey]



    return jsonify(MaxCat)

def convert_to_float(frac_str):
    try:
        return float(frac_str)
    except ValueError:
        num, denom = frac_str.split('/')
        try:
            leading, num = num.split(' ')
            whole = float(leading)
        except ValueError:
            whole = 0
        frac = float(num) / float(denom)
        return whole - frac if whole < 0 else whole + frac