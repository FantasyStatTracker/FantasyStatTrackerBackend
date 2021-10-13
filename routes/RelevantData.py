from flask import Blueprint, render_template, jsonify
import requests
import yahoo_fantasy_api as yfa
from yahoo_oauth import OAuth2
from collections import OrderedDict
from flask_cors import CORS, cross_origin
from Variables.TokenRefresh import oauth, gm, lg




RelevantData = Blueprint('RelevantData', __name__)

#Maps unique team ID to team name
@RelevantData.route('/teammap', methods=['GET']) #data
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


@RelevantData.route("/schedule", methods=['GET']) #schedule (not needed anymore really)
def getSchedule():
    year = "2021"
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

    return Game


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






