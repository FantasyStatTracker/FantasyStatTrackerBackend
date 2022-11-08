from Model.variable import MatchupHistory, db
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import json
from Variables.TokenRefresh import api_key
from .FullData import get_current_week, test
from .WinningMatchup import winning, get_wins
from HelperMethods.helper import get_league_matchups
from .Prediction import predict

Admin = Blueprint("Admin", __name__)


@Admin.route("/initialize-new-season", methods=["GET"])
@cross_origin()
def initialize_season():
    headers = request.headers
    auth = headers.get("X-Api-Key")

    if auth == api_key:
        get_league_matchups()

    else:
        return jsonify({"message": "ERROR: unauthorized"}), 401

    return "nothing"


@Admin.route("/update-previous-week", methods=["GET"])  # winning
@cross_origin()
def update_roster_stats():
    headers = request.headers
    auth = headers.get("X-Api-Key")

    if auth == api_key:

        previous_week = int(get_current_week()) - 1
        if previous_week == 0:
            return "Nothing to predict for week 1"
        previous_week_data = test(previous_week).get_data()
        print(previous_week_data)
        previous_winning_matchups = (
            winning(previous_week_data).get_data().decode("utf-8")
        )
        previous_leaders = get_wins(previous_week_data).get_data().decode("utf-8")
        previous_week_data = previous_week_data.decode("utf-8")
        previous_week_data = json.loads(previous_week_data)["team_data"]

        matchup_record = MatchupHistory(
            matchup_week=previous_week,
            all_data=json.dumps(previous_week_data),
            winning_matchup=previous_winning_matchups,
            leader=previous_leaders,
        )
        db.session.add(matchup_record)
        db.session.commit()

        get_league_matchups()

        # predict()

    else:
        return jsonify({"message": "ERROR: unauthorized"}), 401

    return "Update Complete"
