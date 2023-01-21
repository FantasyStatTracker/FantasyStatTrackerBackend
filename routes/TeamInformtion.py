import collections
import json
from flask import Blueprint, jsonify
from flask_cors import CORS
from Model.variable import Variable
from HelperMethods.helper import get_team_map, get_team_id_to_name_map
from Variables.TokenRefresh import lg
from cache import cache

TeamInformation = Blueprint("TeamInformation", __name__)
cors = CORS(TeamInformation)


@TeamInformation.route("/team-injury", methods=["GET"])
@cache.cached()
def get_team_injury_data():
    r = get_team_map()
    res = {}
    tm = list(lg.teams().keys())
    for x in tm:
        team = r[x]
        res[team] = {}
        tm1 = lg.to_team(x).roster()

        for y in tm1:
            if y["status"] != "":
                res[team][y["name"]] = y["status"]

    return res


@TeamInformation.route("/transactions", methods=["GET"])
def get_waiver_pickup():
    res = {}
    r = get_team_map()
    for team in r.values():
        res[team] = {}

    for team in r:

        league_add_drop_information = lg.transactions("add", "")
        for transaction in league_add_drop_information:

            transaction_type = transaction["type"]
            player_name = ""
            transaction_team_id = ""
            transaction_executed_on_player = ""
            if transaction_type == "add":
                full_data_array = transaction["players"]["0"]["player"]
                player_name = full_data_array[0][2]["name"]["full"]
                transaction_team_id = full_data_array[1]["transaction_data"][0][
                    "destination_team_key"
                ]
                transaction_executed_on_player = full_data_array[1]["transaction_data"][
                    0
                ]["type"]

            elif transaction_type == "drop":
                full_data_array = transaction["players"]["0"]["player"]
                player_name = full_data_array[0][2]["name"]["full"]
                transaction_team_id = full_data_array[1]["transaction_data"][
                    "source_team_key"
                ]
                transaction_executed_on_player = full_data_array[1]["transaction_data"][
                    "type"
                ]
            elif transaction_type == "add/drop":  # two transactions, response is weird

                full_data_array = transaction["players"]["0"]["player"]
                player_name = full_data_array[0][2]["name"]["full"]
                transaction_team_id = full_data_array[1]["transaction_data"][0][
                    "destination_team_key"
                ]
                transaction_executed_on_player = full_data_array[1]["transaction_data"][
                    0
                ]["type"]

                ##############

                full_data_array = transaction["players"]["1"]["player"]
                player_name = full_data_array[0][2]["name"]["full"]
                transaction_team_id = full_data_array[1]["transaction_data"][
                    "source_team_key"
                ]
                transaction_executed_on_player = full_data_array[1]["transaction_data"][
                    "type"
                ]

            res[r[transaction_team_id]][player_name] = transaction_executed_on_player

    return jsonify(res)


@TeamInformation.route("/v2/transactions", methods=["GET"])
@cache.cached()
def get_waiver_pickup_v2():
    res = {}
    r = get_team_map()
    for team in r.values():
        res[team] = {}

    for team in r:

        league_add_drop_information = lg.transactions("add", "10")

        for transaction in league_add_drop_information:
            transaction_type = transaction["type"]
            timestamp = transaction["timestamp"]
            player_name = ""
            transaction_team_id = ""
            transaction_executed_on_player = ""
            if transaction_type == "add":
                full_data_array = transaction["players"]["0"]["player"]
                player_name = full_data_array[0][2]["name"]["full"]
                transaction_team_id = full_data_array[1]["transaction_data"][0][
                    "destination_team_key"
                ]
                transaction_executed_on_player = full_data_array[1]["transaction_data"][
                    0
                ]["type"]

            elif transaction_type == "drop":
                full_data_array = transaction["players"]["0"]["player"]
                player_name = full_data_array[0][2]["name"]["full"]
                transaction_team_id = full_data_array[1]["transaction_data"][
                    "source_team_key"
                ]
                transaction_executed_on_player = full_data_array[1]["transaction_data"][
                    "type"
                ]

            elif transaction_type == "add/drop":  # two transactions, response is weird

                full_data_array = transaction["players"]["0"]["player"]
                player_name = full_data_array[0][2]["name"]["full"]
                transaction_team_id = full_data_array[1]["transaction_data"][0][
                    "destination_team_key"
                ]
                transaction_executed_on_player = full_data_array[1]["transaction_data"][
                    0
                ]["type"]
                res[r[transaction_team_id]][int(timestamp)] = {
                    "transaction": transaction_executed_on_player,
                    "player_name": player_name,
                }
                ##############

                full_data_array = transaction["players"]["1"]["player"]
                player_name = full_data_array[0][2]["name"]["full"]
                transaction_team_id = full_data_array[1]["transaction_data"][
                    "source_team_key"
                ]
                transaction_executed_on_player = full_data_array[1]["transaction_data"][
                    "type"
                ]

            res[r[transaction_team_id]][int(timestamp)] = {
                "transaction": transaction_executed_on_player,
                "player_name": player_name,
            }

    for x in res:
        collections.OrderedDict(sorted(res[x].items(), reverse=True))

    return jsonify(res)


@TeamInformation.route("/v2", methods=["GET"])
def test():
    return jsonify(lg.transactions("add", ""))


@TeamInformation.route("/league/streak", methods=["GET"])
def get_team_streak():
    team_map = get_team_map()
    streak_response = json.loads(
        Variable.query.filter_by(variable_name="Streak").first().variable_data
    )

    # Convert to Frontend readable
    for x in team_map:
        streak_response[team_map[x]] = streak_response[x]
    for x in team_map:
        del streak_response[x]

    return jsonify(streak_response)


@TeamInformation.route("/league/average", methods=["GET"])
def get_league_average():
    league_average = json.loads(
        Variable.query.filter_by(variable_name="League_Average").first().variable_data
    )

    return jsonify(league_average)


@TeamInformation.route("/league/overall/average", methods=["GET"])
def get_league_overall_average():
    league_overall_average = json.loads(
        Variable.query.filter_by(variable_name="League_Average").first().variable_data
    )

    return jsonify(league_overall_average)


@TeamInformation.route("/team-map", methods=["GET"])
def get_team_map_inv():

    return jsonify(get_team_map())
