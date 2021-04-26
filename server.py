from yahoo_oauth import OAuth2
import sys

import json
import yahoo_fantasy_api as yfa
from flask import Flask, request, jsonify, redirect
from flask_cors import CORS, cross_origin
import os
from collections import OrderedDict
import requests
from operator import itemgetter
import subprocess
import _pickle as cPickle
from TeamPlayer import Q, WeeklyStat
from Schedule2021 import *


oauth = OAuth2(None, None, from_file='oauth2.json')

if not oauth.token_is_valid():
    oauth.refresh_access_token()

gm = yfa.Game(oauth, 'nba')
lg = gm.to_league('402.l.67232')



app = Flask(__name__)
cors = CORS(app)
statMap = {"5": "FG%", "8":"FT%", "10":"3PTM", "12":"PTS", "15":"REB", "16":"AST", "17":"ST", "18":"BLK", "19":"TO"}
TeamMap = {
    "402.l.67232.t.1": "Feng's Unreal Team",
    "402.l.67232.t.10": "Liam's Team",
    "402.l.67232.t.11": "Team Goon Cena",
    "402.l.67232.t.12": "what time? Dame time",
    "402.l.67232.t.2": "Donutcic",
    "402.l.67232.t.3": "Coomers Assemble",
    "402.l.67232.t.4": "EMVBiid",
    "402.l.67232.t.5": "Kentuckyy",
    "402.l.67232.t.6": "I stan curry uwu",
    "402.l.67232.t.7": "David's Team",
    "402.l.67232.t.8": "Sufyan's Super Team",
    "402.l.67232.t.9": "Joseph Ingles"
}

@app.route('/')
@cross_origin()
def index():
    return ""

@app.route('/teammap', methods=['GET'])

def getTeamMap():

    matchupInfo = lg.matchups()
    teams = OrderedDict()
    data = matchupInfo["fantasy_content"]["league"][1]["scoreboard"]["0"]["matchups"]
    matchupKey = list(data.keys())
    matchupKey = matchupKey[:-1]

    teamMap = {}
    teamFGFT = {}
    current = ""
    for matchupIndex in matchupKey:
        for matchupIndividualTeam in range(0,2): #matchup will always have two people
            for TeamData in data[matchupIndex]["matchup"]["0"]["teams"][str(matchupIndividualTeam)]["team"]:
                try:

                    teamMap[TeamData[0]['team_key']] = TeamData[2]['name']
                except:
                    try:
                        print(teamMap.keys())
                        print(TeamData["team_stats"]["stats"][0]['stat']['value'], TeamData["team_stats"]["stats"][2]['stat']['value'])
                    except:
                         continue
    
                    
    print(teamMap)
    return teamMap 

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

@app.route('/FG', methods=['GET'])
def getFGFT():

    matchupInfo = lg.matchups(lg.current_week()-1)
    teams = OrderedDict()
    data = matchupInfo["fantasy_content"]["league"][1]["scoreboard"]["0"]["matchups"]
    matchupKey = list(data.keys())
    matchupKey = matchupKey[:-1]


    print(data)

    teamFGFT = {}
    current = ""
    tempVar = ""
    for matchupIndex in matchupKey:
        for matchupIndividualTeam in range(0,2): #matchup will always have two people
            for TeamData in data[matchupIndex]["matchup"]["0"]["teams"][str(matchupIndividualTeam)]["team"]:
                try:

                    tempVar = TeamData[0]['team_key']
                except:
                    try:
                        teamFGFT[tempVar] = [
                            convert_to_float(TeamData["team_stats"]["stats"][0]['stat']['value']), 
                            convert_to_float(TeamData["team_stats"]["stats"][2]['stat']['value'])
                        ]
                        

                       
                    except:
                         continue

                
                        
                    
                    
    print(teamFGFT)
    return teamFGFT

def getMatchups():
    
    matchupInfo = lg.matchups()
    teams = OrderedDict()
    data = matchupInfo["fantasy_content"]["league"][1]["scoreboard"]["0"]["matchups"]
    matchupKey = list(data.keys())
    matchupKey = matchupKey[:-1]


    P1 = ""
    Matchup = {}
    current = ""
    for matchupIndex in matchupKey:
        for matchupIndividualTeam in range(0,2): #matchup will always have two people
            for index, TeamData in enumerate(data[matchupIndex]["matchup"]["0"]["teams"][str(matchupIndividualTeam)]["team"]):
  
                try:

                    if (matchupIndividualTeam == 0):
                        P1 = TeamData[0]['team_key']
                    else:
                        Matchup[P1] = TeamData[0]['team_key']
                except:
                    continue
                    
                
    print(Matchup)
                

    return Matchup
    
@app.route('/full', methods=['GET'])
def getAll():
    return lg.matchups()


@app.route('/last', methods=['GET'])
def getLastWeek():

    return jsonify(lg.player_stats(6030, 'lastweek'))

'''    
ketuck
"FG%": 0.48747591522157996,
"FT%": 0.8518518518518519,
donut
"FG%": 0.5085836909871244,
"FT%": 0.6791044776119403,
Emv 
 "FG%": 0.4581673306772908,
"FT%": 0.8629032258064516,
davids
 "FG%": 0.44288577154308617,
"FT%": 0.8415841584158416,
'''
@app.route('/predict', methods=['GET'])
def predict():
    if not oauth.token_is_valid():
        oauth.refresh_access_token()
    count = 0
    weekRange = (lg.week_date_range(lg.current_week()))


    a = {"PTS": 0.0, "FG%": 0.0, "AST": 0.0, "FT%": 0.0, "3PTM": 0.0, "ST": 0.0, "BLK": 0.0, "TO": 0.0, "REB": 0.0}

    L = []
    Schedule = []
    teams = lg.teams()
    print("teams", teams)
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
        a = {"PTS": 0.0, "FG%": 0.0, "AST": 0.0, "FT%": 0.0, "3PTM": 0.0, "ST": 0.0, "BLK": 0.0, "TO": 0.0, "REB": 0.0}

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
        
        print("\n")
        
    print(StatPrediction)

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
    
    





@app.route("/schedule", methods=['GET'])
def getSchedule():
    r = requests.get('https://data.nba.com/data/10s/v2015/json/mobile_teams/nba/2020/league/00_full_schedule.json')

    Game = {}
    data = r.json()

    for x in data['lscd']:
        Game[x["mscd"]["mon"]] = {}
        
        
        for y in x["mscd"]["g"]:
            Game[x["mscd"]["mon"]][y["gdte"]] = []
        for y in x["mscd"]["g"]:
            Game[x["mscd"]["mon"]][y["gdte"]].append((y["v"]["ta"], y["h"]["ta"]))

    return Game
    

@app.route('/win-calculator', methods=['POST'])
@cross_origin()
def getWins():


    if not oauth.token_is_valid():
        oauth.refresh_access_token()

    data = json.loads(request.form.get("data"))
    categoryMax = {"FG%":{}, "FT%":{}, "3PTM":{},"PTS":{}, "REB":{}, "AST":{}, "ST":{}, "BLK":{}, "TO":{}}
    
    for x in data:
        
        for y in list(x.keys()): #team stats
            
            for z in x[y].keys(): #cats
                try:
                    categoryMax[z][y] = float(x[y][z])
                except:
                    categoryMax[z][y] = 0

    catSort = {}
    for x in categoryMax:
        sortedCategory = (sorted(categoryMax[x].items(), key=itemgetter(1), reverse=True))
        catSort[x] = sortedCategory
                
    return catSort


@app.route('/fix', methods=['GET'])
def fix():
    Fix = WeeklyStat

    for team in Fix:
        for player in Fix[team]:
            player[0]["team"] = player[1]
            del(player[1])
    
    return Fix

@app.route('/playoff', methods=['GET'])
@cross_origin()
def playoff():
    oauth = OAuth2(None, None, from_file='oauth2.json')

    if not oauth.token_is_valid():
        oauth.refresh_access_token()

    teams = OrderedDict()


    matchupInfo = lg.matchups()
    


    #roster
    info = {}
    roster = {}
    league = {}

    
    for x in lg.teams():
        
        
        roster[x] = []

        for y in lg.to_team(x).roster():
           
            item = lg.player_stats(y["player_id"], 'lastweek')
            item.append(lg.player_details(y["player_id"])[0]["editorial_team_abbr"])
            roster[x].append(item)

 
    
    return roster 
    
@app.route('/test', methods=['GET'])
@cross_origin()
def test():

   

    if not oauth.token_is_valid():
        oauth.refresh_access_token()

    teams = OrderedDict()

    matchupInfo = lg.matchups()

    data = matchupInfo["fantasy_content"]["league"][1]["scoreboard"]["0"]["matchups"]
    
    matchupKey = list(data.keys())
    matchupKey = matchupKey[:-1]

    current = ""
    for matchupIndex in matchupKey:
        print(matchupIndex)
        for matchupIndividualTeam in range(0,2): #matchup will always have two people
            for TeamData in data[matchupIndex]["matchup"]["0"]["teams"][str(matchupIndividualTeam)]["team"]:
                if (isinstance(TeamData, list)):
                    teams[TeamData[2]["name"]] = {}
                    current = TeamData[2]["name"]
            for statInformation in data[matchupIndex]["matchup"]["0"]["teams"][str(matchupIndividualTeam)]["team"][1]["team_stats"]["stats"]:
                try:
                    if (statInformation["stat"]["value"] == ""):
                        teams[current][(statMap[statInformation["stat"]["stat_id"]])] = 0
                    else:
                        teams[current][(statMap[statInformation["stat"]["stat_id"]])] = statInformation["stat"]["value"]
                except:
                    continue

    return teams

@app.route('/winning-matchups', methods=['POST'])
@cross_origin()
def winning():
    data = json.loads(request.form.get("data"))
    currentWins = {}

    for x in data:
        print(x)
        for player1 in list(x.keys()): #team stats
            currentWins[player1] = []
            for y in data:
                for player2 in list(y.keys()):
                    
                    if (player1 == player2):
                        continue
    
                    winCount = 0
                    catWins = []


                        
                    print(player1, player2)
                    if (float(x[player1]['TO']) < float(y[player2]['TO'])): #different condition for Turnovers
                        winCount+=1
                        catWins.append('TO')
                    for z in x[player1].keys(): #cats
                            
                            
                        comp = float(x[player1][z]) > float(y[player2][z])
                        if (comp and z != 'TO'): #check how many wins
                            winCount+=1
                            catWins.append(z)
                           
                                

                    if (winCount >= 5): 
                        currentWins[player1].append({player2: catWins}) #

                    

    print(currentWins)
    return currentWins #json object with Team { Wins { Categorieswon

   

if __name__ == '__main__':
    dev = True
    portVar = ""
    if (dev):
        portVar = 8000
    else:
        portVar = os.environ.get('PORT', 80)
    app.run(host="localhost", port=portVar, debug=dev)