from yahoo_oauth import OAuth2
import sys

import json
import yahoo_fantasy_api as yfa
from flask import Flask, request, jsonify, redirect
from flask_cors import CORS, cross_origin
import os
from collections import OrderedDict

from operator import itemgetter
import subprocess
import _pickle as cPickle


oauth = OAuth2(None, None, from_file='oauth2.json')

if not oauth.token_is_valid():
    oauth.refresh_access_token()

gm = yfa.Game(oauth, 'nba')
lg = gm.to_league('402.l.67232')


app = Flask(__name__)
cors = CORS(app)
statMap = {"5": "FG%", "8":"FT%", "10":"3PTM", "12":"PTS", "15":"REB", "16":"AST", "17":"ST", "18":"BLK", "19":"TO"}

@app.route('/')
@cross_origin()
def index():
    return ""

@app.route('/matchups', methods=['GET'])
def getMatchups():
    
    matchupInfo = lg.matchups()
    return matchupInfo

    

@app.route('/win-calculator', methods=['POST'])
@cross_origin()
def getWins():

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
    
@app.route('/test', methods=['GET'])
@cross_origin()
def test():

    if not oauth.token_is_valid(): #just run this to keep everything working
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
        for player1 in list(x.keys()): #team stats
            currentWins[player1] = []
            for y in data:
                for player2 in list(y.keys()):
                    
                    if (player1 == player2):
                        continue
    
                    winCount = 0
                    catWins = []

                    try:
                        
                        toComp = float(x[player1]['TO']) < float(x[player1]['TO'])
                        if (toComp): #different condition for Turnovers
                            winCount+=1
                            catWins.append('TO')
                        for z in x[player1].keys(): #cats
                            
                            try:
                                comp = float(x[player1][z]) > float(y[player2][z])
                                if (comp and z != 'TO'): #check how many wins
                                    winCount+=1
                                    catWins.append(z)
                            except:
                                x[player][z] = 0
                                y[player][z] = 0
                                

                        if (winCount >= 5): 
                            currentWins[player1].append({player2: catWins}) #

                    except:
                        x[player1]['TO'] = 0
                        x[player1]['TO'] = 0

    return currentWins #json object with Team { Wins { Categorieswon

   

if __name__ == '__main__':
    dev = True
    portVar = ""
    if (dev):
        portVar = 8000
    else:
        portVar = os.environ.get('PORT', 80)
    app.run(host="localhost", port=portVar, debug=dev)