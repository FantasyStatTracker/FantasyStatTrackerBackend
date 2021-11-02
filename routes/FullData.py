from Model.variable import MatchupHistory, db
from flask import Blueprint, render_template, jsonify, request
import flask
import yahoo_fantasy_api as yfa
import json
from collections import OrderedDict
from flask_cors import CORS, cross_origin
from Variables.TokenRefresh import oauth, gm, lg
from Variables.LeagueInformation import statMap


FullData = Blueprint('FullData', __name__)

cors = CORS(FullData)



# GET Returns current week team stats by category
# POST Returns week by week number passed
@FullData.route('/test', methods=['GET', 'POST'])
@cross_origin()
def test(*args):
    teamPhoto = {}
    matchupInfo = None
    if (flask.request.method == 'POST'):  # if requesting a previous week

        week = json.loads(request.form.get("week"))
        PlayerList = MatchupHistory.query.filter_by(matchup_week=week).first()

        return {"AllData": PlayerList.all_data, "Leader": PlayerList.leader, "WinningMatchup": PlayerList.winning_matchup, "WeekNumber": week}

    if not oauth.token_is_valid():
        oauth.refresh_access_token()

    
    #when updating database, optional argument
    weekNumber = None
    try:
        weekNumber = args[0]
    except:
        pass


    matchupInfo = lg.matchups(week=weekNumber)

    teams = OrderedDict()
    data = matchupInfo["fantasy_content"]["league"][1]["scoreboard"]["0"]["matchups"]

    matchupKey = list(data.keys())[:-1]

    current = ""
    for matchupIndex in matchupKey:  # O(n)
        # matchup will always have two people
        for matchupIndividualTeam in range(0, 2):  # O(2)

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

    return {"TeamData": teams, "TeamPhoto": teamPhoto}


# Returns League Average Stats
@FullData.route('/average', methods=['POST'])
@cross_origin()
def getStatAverage():
    categoryArray = json.loads(getCategory().data)
    average = {category: 0.0 for category in categoryArray}
    data = json.loads(request.form.get("data"))
    numberOfTeams = len(data)

    for team in data:  # O(n)
        for teamName in team.keys():  # O(1)
            for category in average.keys():  # O(m)
                average[category] += float(team[teamName][category])

    average = {cat: round(average[cat]/(numberOfTeams), 3) for cat in average}

    return jsonify(average)

# Get All Categories in League


@FullData.route('/category', methods=['GET'])
def getCategory():
    categoryArray = [x for x in statMap.values()]
    return jsonify(categoryArray)

# Get Current Week


@FullData.route('/week', methods=['GET'])
def getWeekTotal():
    return str(lg.current_week())
