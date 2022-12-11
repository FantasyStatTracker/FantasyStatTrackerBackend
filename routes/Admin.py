import datetime
from Model.variable import MatchupHistory, Variable, db
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import json
from Variables.TokenRefresh import api_key, lg
from .FullData import get_current_week, test
from .WinningMatchup import winning, get_wins
from HelperMethods.helper import get_league_matchups

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
        update_streak()

        # predict()

    else:
        return jsonify({"message": "ERROR: unauthorized"}), 401

    return "Update Complete"


def update_streak():

    item = Variable.query.filter_by(variable_name="Streak").first()

    current_streak_data = json.loads(item.variable_data)

    winner = []
    all_team_keys = lg.teams().keys()
    matchup_list_dict = lg.matchups(lg.current_week() - 1)["fantasy_content"]["league"][
        1
    ]["scoreboard"]["0"]["matchups"]

    for matchup_index in matchup_list_dict:  # determine winners
        try:
            matchup_winner = matchup_list_dict[str(matchup_index)]["matchup"][
                "winner_team_key"
            ]
            winner.append(matchup_winner)
        except:  # skip count key error
            continue

    for team_id in winner:  # update team win streaks
        streak = current_streak_data[team_id]["streak"]
        if streak < 0:
            streak = 1
        else:
            streak += 1

        current_streak_data[team_id]["streak"] = streak

    loser = list(set(all_team_keys) - set(winner))

    for team_id in loser:  # update team losing streaks
        streak = current_streak_data[team_id]["streak"]
        if streak > 0:
            streak = -1
        else:
            streak -= 1

        current_streak_data[team_id]["streak"] = streak

    item.variable_data = json.dumps(current_streak_data)
    item.update_at = datetime.datetime.now()
    db.session.commit()

    return current_streak_data
