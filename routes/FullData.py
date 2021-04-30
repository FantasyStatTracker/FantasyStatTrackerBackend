from flask import Blueprint, render_template, jsonify
import yahoo_fantasy_api as yfa

from collections import OrderedDict
from flask_cors import CORS, cross_origin
from Variables.TokenRefresh import oauth, gm, lg
from Variables.LeagueInformation import statMap



FullData = Blueprint('FullData', __name__)
cors = CORS(FullData)


@FullData.route('/test', methods=['GET']) #all data
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
        # matchup will always have two people
        for matchupIndividualTeam in range(0, 2):

            for TeamData in data[matchupIndex]["matchup"]["0"]["teams"][str(matchupIndividualTeam)]["team"]:
                if (isinstance(TeamData, list)):
                    teams[TeamData[2]["name"]] = {}
                    current = TeamData[2]["name"]
            for statInformation in data[matchupIndex]["matchup"]["0"]["teams"][str(matchupIndividualTeam)]["team"][1]["team_stats"]["stats"]:
                try:
                    if (statInformation["stat"]["value"] == ""):
                        teams[current][(
                            statMap[statInformation["stat"]["stat_id"]])] = 0
                    else:
                        teams[current][(
                            statMap[statInformation["stat"]["stat_id"]])] = statInformation["stat"]["value"]
                except:
                    continue

    return teams