from flask import Blueprint, jsonify, request
import requests
from flask_cors import cross_origin
from Variables.TokenRefresh import oauth, lg, api_key
from pytz import timezone
import json
import datetime
from Model.variable import Variable, db


RelevantData = Blueprint("RelevantData", __name__)


year = "2021"
PLAYERLIST = []

# Get all data for current season
@RelevantData.route("/full-player-data", methods=["GET"])  # run once per year
@cross_origin()
def get_full_player_data():
    headers = request.headers
    auth = headers.get("X-Api-Key")

    if auth == api_key:
        r = requests.get("https://data.nba.net/10s/prod/v1/" + year + "/players.json")
    else:
        return jsonify({"message": "ERROR: unauthorized"}), 401
    return r.json()


# not used
@RelevantData.route("/time-to-update", methods=["GET"])
def get_time_to_update():
    global PLAYERLIST

    if isinstance(PLAYERLIST, list):

        PLAYERLIST = Variable.query.filter_by(variable_name="CurrentRoster").first()
    return str(
        int(
            (
                1800
                - abs(PLAYERLIST.updated_at - datetime.datetime.now()).total_seconds()
            )
            / 60
        )
    )


# not working
@RelevantData.route(
    "/team-player-data", methods=["GET"]
)  # run once per week maybe more
def get_last_week_roster():  # Over 10x faster because of list comprehension

    if not oauth.token_is_valid():
        oauth.refresh_access_token()

    # roster
    roster = {}

    for team in lg.teams():

        roster[team] = []

        _ = timezone("EST")
        item = lg.player_stats(
            [x["player_id"] for x in lg.to_team(team).roster()], "lastweek", 2021
        )
        status = [y["status"] for y in lg.to_team(team).roster()]

        for x, y in zip(item, status):
            x["status"] = y

        roster[team] = item

    prediction_roster = Variable.query.filter_by(
        variable_name="PredictionStats"
    ).first()
    prediction_roster.variable_data = json.dumps(roster)
    db.session.commit()

    return roster
