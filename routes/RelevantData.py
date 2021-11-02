from flask import Blueprint, jsonify, request
import requests
from yahoo_oauth import OAuth2
from collections import OrderedDict
from flask_cors import cross_origin
from Variables.TokenRefresh import oauth, lg, apiKey
from pytz import timezone
import json
from routes.holdername import StatCum, Week1, Week2

RelevantData = Blueprint('RelevantData', __name__)

from Model.variable import Variable, db
year = "2021"
#Maps unique team ID to team name

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
        # matchup will always have two people
        for matchupIndividualTeam in range(0, 2):
            for TeamData in data[matchupIndex]["matchup"]["0"]["teams"][str(matchupIndividualTeam)]["team"]:
                try:

                    teamMap[TeamData[0]['team_key']] = TeamData[2]['name']
                except:

                    continue
 

    return teamMap


@RelevantData.route("/schedule", methods=['GET']) #Run once per year
def getSchedule():
    headers = request.headers
    auth = headers.get("X-Api-Key")

    if (auth == apiKey):
        r = requests.get(
            'https://data.nba.com/data/10s/v2015/json/mobile_teams/nba/' + year + '/league/00_full_schedule.json')

        Game = {}
        data = r.json()

        for x in data['lscd']:
            Game[x["mscd"]["mon"]] = {}

            for y in x["mscd"]["g"]:
                Game[x["mscd"]["mon"]][y["gdte"]] = []
            for y in x["mscd"]["g"]:
                Game[x["mscd"]["mon"]][y["gdte"]].append(
                    (y["v"]["ta"], y["h"]["ta"]))
    else:
        return jsonify({"message":"ERROR: unauthorized"}), 401

    with open('./Variables/Schedule2021.py', 'w') as fo:
        fo.write("Sched =" + json.dumps(Game))
        fo.close
    return Game

@RelevantData.route('/matchup', methods=['GET']) #run once per week
def getMatchups(): #predict

    headers = request.headers
    auth = headers.get("X-Api-Key")

    if (auth == apiKey):
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
    else:
        return jsonify({"message":"ERROR: unauthorized"}), 401

    Prediction = Variable.query.filter_by(variable_name="WeekMatchup").first()
    Prediction.variable_data= json.dumps(Matchup)
    db.session.commit()
        
    return Matchup

#Get all data for current season
@RelevantData.route('/full-player-data', methods=['GET']) #run once per year
@cross_origin()
def getFullPlayerData():
    headers = request.headers
    auth = headers.get("X-Api-Key")

    if (auth == apiKey):
        r  = requests.get('https://data.nba.net/10s/prod/v1/'+ year +'/players.json')
    else:
        return jsonify({"message":"ERROR: unauthorized"}), 401
    return r.json()



@RelevantData.route('/team-player-data', methods=['GET']) #run once per week maybe more
def playoff():
    headers = request.headers
    auth = headers.get("X-Api-Key")

    if (auth == apiKey):
        oauth = OAuth2(None, None, from_file='oauth2.json')

        if not oauth.token_is_valid():
            oauth.refresh_access_token()

        teams = OrderedDict()

        matchupInfo = lg.matchups()

        # roster
        info = {}
        roster = {}
        league = {}

        for x in lg.teams():

            roster[x] = []

            for y in lg.to_team(x).roster():

                item = lg.player_stats(y["player_id"], 'season', 2021)[0]
                item["team"] = lg.player_details(y["player_id"])[0]["editorial_team_abbr"]
                item["status"] = y["status"]
                roster[x].append(item)
                
            

    else:
        return jsonify({"message":"ERROR: unauthorized"}), 401

        
    with open('./Variables/TeamPlayer.py', 'w') as fo:
        fo.write("Q =" + json.dumps(roster))
        fo.close
    return roster


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

def currentRoster(): #Over 10x faster because of list comprehension
    from datetime import datetime
    if not oauth.token_is_valid():
        oauth.refresh_access_token()

    # roster
    info = {}
    roster = {}
    league = {}

    for team in lg.teams():

        roster[team] = []
        
        est = timezone('EST')
        item = lg.player_stats([x["player_id"] for x in lg.to_team(team).roster()], 'lastweek', datetime.now(est), 2021)
        status = [y["status"] for y in lg.to_team(team).roster()]

        for x, y in zip(item, status):
            x["status"] = y

        roster[team]=item
        
    return roster

@RelevantData.route('/team-player-dataa', methods=['GET']) #run once per week maybe more
def lastWeekRoster(): #Over 10x faster because of list comprehension
    
    if not oauth.token_is_valid():
        oauth.refresh_access_token()

    # roster
    info = {}
    roster = {}
    league = {}

    for team in lg.teams():

        roster[team] = []
        
        est = timezone('EST')
        #item = lg.player_stats([x["player_id"] for x in lg.to_team(team).roster()], 'lastweek', 2021)
        item = lg.player_stats([x["player_id"] for x in lg.to_team(team).roster()],  'lastweek', 2021)
        status = [y["status"] for y in lg.to_team(team).roster()]

        for x, y in zip(item, status):
            x["status"] = y

        roster[team]=item
    '''
    item = Variable(variable_name='PredictionStats', variable_data=json.dumps(roster))
    db.session.add(item)
    db.session.commit()
    '''
    return roster

@RelevantData.route('/tcum', methods=['GET']) #run once per week maybe more
def lastWeekRosterrr(): #Over 10x faster because of list comprehension
    average = ["PTS", "AST",
               "3PTM", "ST", "BLK", "TO", "REB"]
    
    #SeasonStat = lastWeekRosterr()
    #Prediction = Variable.query.filter_by(variable_name="StatCumulative").first()
    #StatCumulate = Prediction.variable_data

    
    for team1, team2 in zip(Week1, Week2):
        for player1, addToPlayer2 in zip(sorted(Week1[team1], key=lambda d: d["name"]), sorted(Week2[team2], key=lambda d: d["name"])):
            print(player1)
            for cat in average:
                
                try:
                    
                    if (player1["name"] == "Ricky Rubio"):
                        print("helrgsjkg")
                        
                    if (player1[cat] == '-'):
                        player1[cat] = 0.0
                    if (addToPlayer2[cat] == '-'):
                        addToPlayer2[cat] = 0.0
                    player1[cat] += addToPlayer2[cat]
                except:
                    print("hello")
                    continue
                
            
    
              
                
                
                    

    return Week1

@RelevantData.route('/changeData', methods=['GET'])
def gg():
    Prediction = Variable.query.filter_by(variable_name="StatCumulative").first()
    Prediction.variable_data = json.dumps(StatCum)
    db.session.commit()
    
    return ""

    