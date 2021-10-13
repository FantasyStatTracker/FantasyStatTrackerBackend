from flask import Blueprint, render_template, jsonify, request
import requests
import yahoo_fantasy_api as yfa
from yahoo_oauth import OAuth2
from collections import OrderedDict
from flask_cors import CORS, cross_origin
from Variables.TokenRefresh import oauth, gm, lg, apiKey
import json


RelevantData = Blueprint('RelevantData', __name__)

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

    with open('./Variables/CurrentMatchup.py', 'w') as fo:
        fo.write("WeekMatchup =" + json.dumps(Matchup))
        fo.close
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
                break

            break
                
            

    else:
        return jsonify({"message":"ERROR: unauthorized"}), 401

        
    with open('./Variables/test.py', 'w') as fo:
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






