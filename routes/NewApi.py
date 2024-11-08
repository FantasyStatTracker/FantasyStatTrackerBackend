import collections
from flask import Blueprint
from flask.json import jsonify
from flask_cors import cross_origin
from Variables.TokenRefresh import oauth, lg, gm, test2
from yahoo_oauth import OAuth2
import yahoo_fantasy_api as yfa
from flask_cors import CORS, cross_origin
import os 

Api = Blueprint("Api", __name__)

cors = CORS(Api)
@Api.before_app_first_request
def run():
    oauth = OAuth2(None, None, from_file="oauth2.json")
    if not oauth.token_is_valid():
        oauth.refresh_access_token()
    gm = yfa.Game(oauth, "nba")
    lg = gm.to_league("454.l.61169")  # 2022-23
    global team_data_global
    team_data_global = test2(lg)

@Api.before_request
def run2():
    oauth = OAuth2(None, None, from_file="oauth2.json")
    if not oauth.token_is_valid():
        oauth.refresh_access_token()

@Api.route("/full-team-data-v2", methods=["GET"])
@cross_origin()
def get_team_data():
    res = {}
    for team_id in team_data_global:
        team_data = team_data_global[team_id]  
        res[team_data.get_name()] = team_data.team_stats.__dict__
    return jsonify(res)

@Api.route("/winning-matchups-v2", methods=["GET"])
@cross_origin()
def get_winning_matchups():
    res = {}
    for team_id in team_data_global:
        team_data = team_data_global[team_id]
        res[team_data.get_name()] = {
            "winning_matchup":[x.jsonify_matchup() for x in team_data.winning_matchup]
        }
    print(res)
    return jsonify(res)


@Api.route("/category-leader-v2", methods=["GET"])
@cross_origin()
def get_category_leaders():
    res = {}
    category_array = []
    for team_id in team_data_global:
        team_data = team_data_global[team_id]
        category_array = team_data.team_stats.get_category_array()
        if len(res) == 0:
            res = {x:{} for x in category_array}

        team_stats_dict = team_data.team_stats.__dict__
        for i, stat in enumerate(team_stats_dict):
            # category in better format needs to be mapped to object attribute
            res[category_array[i]][team_data.team_name] = team_stats_dict[stat]

    return jsonify(res)


@Api.route("/team-photo-v2", methods=["GET"])
@cross_origin()
def get_team_photo():
    res = {}
    for team_id in team_data_global:
        team_data = team_data_global[team_id]
        res[team_data.team_name] = team_data.team_photo_url

    return jsonify(res)
