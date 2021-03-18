from yahoo_oauth import OAuth2
import json
import yahoo_fantasy_api as yfa
from flask import Flask, request, jsonify
import os
from credentials import *

with open('oauth2.json', "w") as f:
   f.write(json.dumps(creds))
oauth = OAuth2(None, None, from_file='oauth2.json')


gm = yfa.Game(oauth, 'nba')
lg = gm.to_league('402.l.67232')
print(gm.league_ids(year=2020))

app = Flask(__name__)
statMap = {"5": "FG%", "8":"FT%", "10":"3PTM", "12":"PTS", "15":"REB", "16":"AST", "17":"ST", "18":"BLK", "19":"TO"}
@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/matchups', methods=['GET'])
def getMatchups():
    matchupInfo = lg.matchups()
    return matchupInfo
    

@app.route('/win-calculator', methods=['POST'])
def getWins():

    data = json.loads(request.form.get("data"))
    print(data)
    
    categoryMax = {"FG%":[0, ""], "FT%":[0, ""], "3PTM":[0, ""],"PTS":[0, ""], "REB":[0, ""], "AST":[0, ""], "ST":[0, ""], "BLK":[0, ""], "TO":[10000, ""]}
    
    for x in data:
        print(x)
        for y in list(x.keys()): #team stats
            print(x[y])
            for z in x[y].keys(): #cats
                print(z)
                print(x[y][z]) #cat value
                print(categoryMax[z][0])


                if (z == "TO"):
                     if (float(x[y][z]) < float(categoryMax[z][0])):
                        categoryMax[z][0] = float(x[y][z])
                        categoryMax[z][1] = y


                if (float(x[y][z]) > float(categoryMax[z][0])):
                    categoryMax[z][0] = float(x[y][z])
                    categoryMax[z][1] = y
    
    return categoryMax
    
@app.route('/test', methods=['GET'])
def test():
    
    teams = {}

    matchupInfo = lg.matchups()
    data = matchupInfo["fantasy_content"]["league"][1]["scoreboard"]["0"]["matchups"]
    
                
    matchupKey = data.keys()

    current = ""
    for y in range(0,6):
        for z in range(0,2):
            for q in data[str(y)]["matchup"]["0"]["teams"][str(z)]["team"]:
                if (isinstance(q, list)):
                    teams[q[2]["name"]] = {}
                    current = q[2]["name"]
            for x in data[str(y)]["matchup"]["0"]["teams"][str(z)]["team"][1]["team_stats"]["stats"]:
                try:
                    teams[current][(statMap[x["stat"]["stat_id"]])] = x["stat"]["value"]
                except:
                    continue

    return teams

@app.route('/winning-matchups', methods=['POST'])
def winning():
    data = json.loads(request.form.get("data"))
    currentWins = {}
    print(data)

    for x in data:
        for player1 in list(x.keys()): #team stats
            currentWins[player1] = []
            for y in data:
                for player2 in list(y.keys()):
                    if (player1 == player2):
                        continue
                    
                    winCount = 0
                    for z in x[player1].keys(): #cats
                        
                        if (winCount >= 5):
                            currentWins[player1].append(player2) 
                            break
                        if (x[player1][z] > y[player2][z]):
                            winCount+=1
                        
    return currentWins

   

if __name__ == '__main__':
    app.run(host="localhost", port=8000, debug=False)