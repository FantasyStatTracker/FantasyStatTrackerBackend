from yahoo_oauth import OAuth2
import json
import yahoo_fantasy_api as yfa
from flask import Flask
'''

with open('oauth2.json', "w") as f:
   f.write(json.dumps(creds))
oauth = OAuth2(None, None, from_file='oauth2.json')



gm = yfa.Game(oauth, 'nba')
lg = gm.to_league('402.l.67232')
print(gm.league_ids(year=2020))
'''
app = Flask(__name__)
statMap = {"5": "FG%", "8":"FT%", "10":"3PTM", "12":"PTS", "15":"REB", "16":"AST", "17":"ST", "18":"BLK", "19":"TO"}
@app.route('/', methods=['GET'])
def getCategories():
    return lg.stat_categories()

@app.route('/matchups', methods=['GET'])
def getMatchups():
    matchupInfo = lg.matchups()
    return matchupInfo["fantasy_content"]["league"][1]["scoreboard"]["0"]["matchups"]

@app.route('/win-calculator', methods=['GET'])
def getWins():
    return ""
    
@app.route('/test', methods=['GET'])
def test():
    with open('output.json') as f:
        data = json.load(f)
    teams = {}
                
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
   

if __name__ == '__main__':
    app.run(host="localhost", port=8000, debug=True)