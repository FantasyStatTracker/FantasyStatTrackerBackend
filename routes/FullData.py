import logging
from Model.variable import MatchupHistory, Variable, db
from flask import Blueprint, jsonify, request
import flask
import json
from collections import OrderedDict
from flask_cors import CORS, cross_origin
from Variables.TokenRefresh import oauth, lg
from Variables.LeagueInformation import stat_map
from HelperMethods.helper import get_team_map
import statistics
import copy

FullData = Blueprint("FullData", __name__)

cors = CORS(FullData)

# GET Returns current week team stats by category
# POST Returns week by week number passed


@FullData.route("/full-team-data", methods=["GET", "POST"])
@cross_origin()
def test(*args):

    team_photo_url = {}
    full_matchup_information = None
    if flask.request.method == "POST":  # if requesting a previous week

        week = json.loads(request.form.get("week"))
        player_list = MatchupHistory.query.filter_by(matchup_week=week).first()

        return {
            "all_data": player_list.all_data,
            "leader": player_list.leader,
            "winning_matchup": player_list.winning_matchup,
            "week_number": week,
        }

    if not oauth.token_is_valid():
        oauth.refresh_access_token()

    # when updating database, optional argument, if None fetches most recent week
    week_number = None
    try:
        week_number = args[0]
    except Exception as e:
        logging.exception(e.__class__.__name__)
        pass

    full_matchup_information = lg.matchups(week=week_number)["fantasy_content"][
        "league"
    ][1]["scoreboard"]["0"]["matchups"]

    teams = OrderedDict()

    matchup_key = list(full_matchup_information.keys())[:-1]

    currently_selected_team = ""
    for matchup_index in matchup_key:  # O(n)
        # matchup will always have two people
        for matchup_individual_team in range(0, 2):

            for team_data in full_matchup_information[matchup_index]["matchup"]["0"][
                "teams"
            ][str(matchup_individual_team)]["team"]:
                if isinstance(team_data, list):
                    teams[team_data[2]["name"]] = {}
                    currently_selected_team = team_data[2]["name"]
                    team_photo_url[team_data[2]["name"]] = team_data[5]["team_logos"][
                        0
                    ]["team_logo"]["url"]

            for stat_information in full_matchup_information[matchup_index]["matchup"][
                "0"
            ]["teams"][str(matchup_individual_team)]["team"][1]["team_stats"]["stats"]:
                try:
                    if (
                        stat_information["stat"]["value"] == ""
                        or stat_information["stat"]["value"] is None
                    ):
                        teams[currently_selected_team][
                            (stat_map[stat_information["stat"]["stat_id"]])
                        ] = 0
                    else:
                        teams[currently_selected_team][
                            (stat_map[stat_information["stat"]["stat_id"]])
                        ] = stat_information["stat"]["value"]
                except Exception as e:
                    logging.info(e)
                    continue

    return {"team_data": teams, "team_photo": team_photo_url}


# Returns League Average Stats
@FullData.route("/average", methods=["POST"])
@cross_origin()
def get_stat_average():
    category_array = json.loads(get_category().data)
    average_per_category = {category: 0.0 for category in category_array}
    team_statistics = json.loads(request.form.get("data"))
    number_of_teams = len(team_statistics)

    for league_team_data in team_statistics:  # O(n)
        for team_name in league_team_data.keys():  # O(1)
            for category in category_array:  # O(m)
                average_per_category[category] += float(
                    league_team_data[team_name][category]
                )

    average_per_category = {
        category: round(average_per_category[category] / (number_of_teams), 3)
        for category in average_per_category
    }

    return jsonify(average_per_category)


@FullData.route("/standard-deviation", methods=["POST"])
@cross_origin()
def get_standard_deviation():
    category_array = json.loads(get_category().data)
    stdev = {category: 0.0 for category in category_array}
    team_statistics = json.loads(request.form.get("data"))

    for category in category_array:
        category_values_array = []
        for league_team_data in team_statistics:
            for team_name in league_team_data.keys():
                category_values_array.append(
                    float(league_team_data[team_name][category])
                )

        stdev[category] = round(statistics.stdev(category_values_array), 3)

    return jsonify(stdev)


# Get All Categories in League


@FullData.route("/category", methods=["GET"])
def get_category():
    category_array = [x for x in stat_map.values()]
    return jsonify(category_array)


# Get Current Week


@FullData.route("/week", methods=["GET"])
def get_current_week():
    return str(lg.current_week())


@FullData.route("/strength", methods=["GET"])
def get_stength():
    total = MatchupHistory.query.filter_by(matchup_week=1).first().all_data
    for x in range(2, 11):
        s = MatchupHistory.query.filter_by(matchup_week=x).first().all_data

        for key1 in total:
            for y in total[key1]:
                total[key1][y] = float(total[key1][y]) + float(s[key1][y])

    for x in total:
        total[x]["FG%"] /= int(get_current_week()) - 1
        total[x]["FG%"] = round(total[x]["FG%"], 2)

        total[x]["FT%"] /= int(get_current_week()) - 1
        total[x]["FT%"] = round(total[x]["FT%"], 3)

    average = copy.deepcopy(total)

    for team in average:
        for cat in average[team]:
            if cat == "FG%" or cat == "FT%":
                continue
            average[team][cat] = float(average[team][cat]) / (
                float(get_current_week()) - 1
            )

    print(len(json.dumps(total)))
    total_week = Variable(variable_name="Average", variable_data=json.dumps(average))
    db.session.add(total_week)
    db.session.commit()

    return jsonify([total, average])


@FullData.route("/overall-strength", methods=["GET"])
def get_thing():
    total = json.loads(
        Variable.query.filter_by(variable_name="Total").first().variable_data
    )
    total_cat = {}
    for x in total:
        for y in total[x].keys():
            total_cat[y] = 0.0
        break

    for x in total:
        for y in total[x]:
            total_cat[y] += total[x][y]

    for x in total_cat:
        total_cat[x] /= len(get_team_map())
        if x != "FG%" or x != "FT%":
            total_cat[x] /= float(get_current_week()) - 1
            total_cat[x] = round(total_cat[x], 3)

    return jsonify(total_cat)

