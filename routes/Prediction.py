from flask import Blueprint, jsonify, request
from routes.RelevantData import get_last_week_roster
from Variables.Schedule2021 import *
from flask_cors import CORS
from Variables.TokenRefresh import oauth, lg
from pytz import timezone
import datetime
import json
from sqlalchemy import text
from HelperMethods.helper import getFGFT, getTeamMap

Prediction_Blueprint = Blueprint("Prediction", __name__)
cors = CORS(Prediction_Blueprint)

from Model.variable import Variable, PredictionHistory, db

TEAM_MAP = []
PLAYER_LIST = []


@Prediction_Blueprint.route("/prediction-fast", methods=["GET"])  # prediction
def get_prediction_fast():
    """
    Prediction = Variable.query.filter_by(variable_name="CurrentPrediction").first()
    sqlQuery = text("select extract(dow from (SELECT updated_at from variable where variable_name='CurrentPrediction'))")
    res = db.engine.execute(sqlQuery)
    day = 0
    for x in res:
        for y,z in x.items():
            day = z
            break
        break
    """

    Prediction = Variable.query.filter_by(variable_name="CurrentPrediction").first()

    return jsonify(Prediction.variable_data)


# Prediction Function
def predict():
    global TEAM_MAP
    global PLAYER_LIST

    if not oauth.token_is_valid():
        oauth.refresh_access_token()

    teams = lg.teams()

    stat_prediction = {}

    if isinstance(
        TEAM_MAP, list
    ):  # update team mapping iff there was a change (10x faster)
        TEAM_MAP = (
            Variable.query.filter_by(variable_name="TeamMap").first().variable_data
        )

    if isinstance(PLAYER_LIST, list):
        PLAYER_LIST = (
            Variable.query.filter_by(variable_name="PredictionStats")
            .first()
            .variable_data
        )

    FGFT = getFGFT()

    # Populate Data
    for team in teams:
        prediction_data = {
            "PTS": 0.0,
            "FG%": 0.0,
            "AST": 0.0,
            "FT%": 0.0,
            "3PTM": 0.0,
            "ST": 0.0,
            "BLK": 0.0,
            "TO": 0.0,
            "REB": 0.0,
        }

        for player in PLAYER_LIST[team]:

            for x in prediction_data.keys():
                try:
                    if player["status"] == "INJ":
                        continue
                    prediction_data[x] += player[x]
                except:
                    continue

            try:
                prediction_data["FG%"] = float(FGFT[team][0])
                prediction_data["FT%"] = float(FGFT[team][1])
            except:
                continue

        stat_prediction[team] = prediction_data

    matchup = (
        Variable.query.filter_by(variable_name="WeekMatchup").first().variable_data
    )

    prediction_array = []

    # Compare Populated Data to Find Winner
    for team in matchup:
        opponent = matchup[team]
        Prediction = {team: 0, opponent: 0}
        for cat1 in stat_prediction[team]:
            if cat1 == "TO":
                if stat_prediction[team][cat1] < stat_prediction[opponent][cat1]:
                    Prediction[team] += 1
                elif stat_prediction[team][cat1] > stat_prediction[opponent][cat1]:
                    Prediction[opponent] += 1
                else:
                    continue
                continue

            if stat_prediction[team][cat1] > stat_prediction[opponent][cat1]:
                Prediction[team] += 1
            elif stat_prediction[team][cat1] < stat_prediction[opponent][cat1]:
                Prediction[opponent] += 1
            else:
                continue

        prediction_array.append(Prediction)

    for x in stat_prediction:
        stat_prediction[x]["FG%"] = round(stat_prediction[x]["FG%"], 3)
        stat_prediction[x]["FT%"] = round(stat_prediction[x]["FT%"], 3)

    return_prediction = []

    for x in prediction_array:
        new_dict = {}
        for match in x.keys():
            new_dict[TEAM_MAP[match]] = [x[match], stat_prediction[match]]
        return_prediction.append(new_dict)

    try:
        item = Variable.query.filter_by(variable_name="CurrentPrediction").first()
        item.variable_data = json.dumps(return_prediction)
        item.updated_at = datetime.datetime.now()
        db.session.commit()
    except:
        print("Entry already exists")

    prediction_item = PredictionHistory(
        prediction_week=lg.current_week(),
        prediction_data=json.dumps(return_prediction),
        prediction_correct=0,
    )
    try:
        db.session.add(prediction_item)
        db.session.commit()
    except:
        print("Entry already Exists")

    return jsonify(return_prediction)


# Returns Team FG% and FT% for the week


# returns top performers per team by category lead
@Prediction_Blueprint.route("/TopPerformers", methods=["POST"])
def get_top_performers():

    global TEAM_MAP
    global PLAYER_LIST

    data = json.loads(request.form.get("team"))
    category_ranking = json.loads(request.form.get("categoryRanking"))
    team_to_fetch = ""

    if isinstance(
        TEAM_MAP, list
    ):  # update team mapping iff there was a change (10x faster)
        TEAM_MAP = Variable.query.filter_by(variable_name="TeamMap").first()

    if data not in TEAM_MAP.variable_data.values():
        new_team_map = getTeamMap()
        TEAM_MAP = Variable.query.filter_by(variable_name="TeamMap").first()
        TEAM_MAP.variable_data = json.dumps(new_team_map)
        db.session.commit()

    if isinstance(PLAYER_LIST, list):

        PLAYER_LIST = Variable.query.filter_by(variable_name="CurrentRoster").first()

    if (abs(PLAYER_LIST.updated_at - datetime.datetime.now()).total_seconds()) > 1800:

        new_roster = get_last_week_roster()
        PLAYER_LIST.variable_data = json.dumps(new_roster)
        PLAYER_LIST.updated_at = datetime.datetime.now()
        db.session.commit()

        PLAYER_LIST = Variable.query.filter_by(variable_name="CurrentRoster").first()

    for x in TEAM_MAP.variable_data:
        if TEAM_MAP.variable_data[x] == data:
            team_to_fetch = x
            break

    maximum_category = {}

    maximum_category = dict.fromkeys(
        category_ranking, {"Value": 0.0, "PlayerFirst": "", "PlayerLast": ""}
    )
    for Player in PLAYER_LIST.variable_data[team_to_fetch]:

        for individual_category in category_ranking:

            if Player[individual_category] == "-":
                Player[individual_category] = 0.0

            if maximum_category[individual_category]["Value"] <= float(
                Player[individual_category]
            ):
                Name = Player["name"].split()
                if Name[0] == "Robert" and Name[1] == "Williams":
                    Name[1] = "Williams III"

                maximum_category[individual_category] = {
                    "Value": float(Player[individual_category]),
                    "PlayerFirst": Name[0],
                    "PlayerLast": " ".join(Name[x] for x in range(1, len(Name))),
                }

    delete = []
    for key in maximum_category:
        if maximum_category[key]["PlayerFirst"] == "":
            delete.append(key)

    for deletion_key in delete:
        del maximum_category[deletion_key]

    return jsonify(maximum_category)

