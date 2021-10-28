from Model.variable import MatchupHistory, db
from flask import Blueprint, render_template, jsonify, request
import flask
import yahoo_fantasy_api as yfa
import json
from collections import OrderedDict
from flask_cors import CORS, cross_origin
from Variables.TokenRefresh import oauth, gm, lg
from Variables.LeagueInformation import statMap

'''
q = MatchupHistory(matchup_week=lg.current_week()-1, all_data=json.dumps(teams))
    db.session.add(q)
    db.session.commit()

    '''
FullData = Blueprint('FullData', __name__)

cors = CORS(FullData)

teamPhoto = {}
# Returns current week team stats by category


@FullData.route('/test', methods=['GET', 'POST'])
@cross_origin()
def test():
    matchupInfo = None
    if (flask.request.method == 'POST'): #if requesting a previous week

        week = json.loads(request.form.get("week"))
        PlayerList = MatchupHistory.query.filter_by(matchup_week=week).first()

        return {"AllData": PlayerList.all_data, "Leader": PlayerList.leader, "WinningMatchup": PlayerList.winning_matchup, "WeekNumber": week}
    else:
        if not oauth.token_is_valid():
            oauth.refresh_access_token()
        matchupInfo = lg.matchups()


    teams = OrderedDict()
    data = matchupInfo["fantasy_content"]["league"][1]["scoreboard"]["0"]["matchups"]

    matchupKey = list(data.keys())[:-1]

    current = ""
    for matchupIndex in matchupKey:
        # matchup will always have two people
        for matchupIndividualTeam in range(0, 2):

            for TeamData in data[matchupIndex]["matchup"]["0"]["teams"][str(matchupIndividualTeam)]["team"]:
                if (isinstance(TeamData, list)):
                    teams[TeamData[2]["name"]] = {}
                    current = TeamData[2]["name"]
                    teamPhoto[TeamData[2]["name"]
                              ] = TeamData[5]["team_logos"][0]["team_logo"]["url"]
            for statInformation in data[matchupIndex]["matchup"]["0"]["teams"][str(matchupIndividualTeam)]["team"][1]["team_stats"]["stats"]:
                try:
                    if (statInformation["stat"]["value"] == "" or statInformation["stat"]["value"] == None):
                        teams[current][(
                            statMap[statInformation["stat"]["stat_id"]])] = 0
                    else:
                        teams[current][(
                            statMap[statInformation["stat"]["stat_id"]])] = statInformation["stat"]["value"]
                except:
                    continue

    return teams

# Returns each teams Yahoo profile picture


@FullData.route('/team-photo', methods=['GET'])
@cross_origin()
def getTeamPhoto():
    if not oauth.token_is_valid():
        oauth.refresh_access_token()

    teams = OrderedDict()

    matchupInfo = lg.matchups()
    data = matchupInfo["fantasy_content"]["league"][1]["scoreboard"]["0"]["matchups"]

    matchupKey = list(data.keys())
    matchupKey = matchupKey[:-1]

    for matchupIndex in matchupKey:
        # matchup will always have two people
        for matchupIndividualTeam in range(0, 2):

            for TeamData in data[matchupIndex]["matchup"]["0"]["teams"][str(matchupIndividualTeam)]["team"]:
                if (isinstance(TeamData, list)):
                    teamPhoto[TeamData[2]["name"]
                              ] = TeamData[5]["team_logos"][0]["team_logo"]["url"]

    return jsonify(teamPhoto)


@FullData.route('/average', methods=['POST'])
@cross_origin()
def getStatAverage():

    average = {"PTS": 0.0, "FG%": 0.0, "AST": 0.0, "FT%": 0.0,
               "3PTM": 0.0, "ST": 0.0, "BLK": 0.0, "TO": 0.0, "REB": 0.0}
    data = json.loads(request.form.get("data"))

    for team in data:
        for teamName in team.keys():
            for category in team[teamName]:
                
                average[category] += float(team[teamName][category])

    average = {cat: round(average[cat]/(len(data)), 3) for cat in average}

    

    
    return jsonify(average)

@FullData.route('/category', methods=['GET'])
def getCategory():
    average = ["PTS", "FG%", "AST", "FT%",
               "3PTM", "ST", "BLK", "TO", "REB"]

    return jsonify(average)
@FullData.route('/week', methods=['GET'])
def getWeekTotal():
    return str(lg.current_week())


