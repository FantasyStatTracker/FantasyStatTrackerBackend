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

stat_map = {
    "5": "FG%",
    "8": "FT%",
    "10": "3PTM",
    "12": "PTS",
    "15": "REB",
    "16": "AST",
    "17": "ST",
    "18": "BLK",
    "19": "TO",
}

stat_array = ["FG", "FT", "ThreePTM", "PTS", "REB", "AST", "ST", "BLK", "TO"]

class LeagueData:
    def __init__(self):
        pass

class TeamStats:
    def __init__(self, **kwargs):
        self.FG = kwargs.get("FG%", None)
        self.FT = kwargs.get("FT%", None)
        self.ThreePTM = kwargs.get("3PTM", None)
        self.PTS = kwargs.get("PTS", None)
        self.REB = kwargs.get("REB", None)
        self.AST = kwargs.get("AST", None)
        self.ST = kwargs.get("ST", None)
        self.BLK = kwargs.get("BLK", None)
        self.TO = kwargs.get("TO", None)

class WinningMatchup:
    def __init__(self, team_name: str, category_won: list):
        self.team_name = team_name
        self.category_won = category_won

class Team:
    def __init__(self, team_stats: TeamStats, team_id: str, team_name: str, team_photo_url: str):
        self.team_stats = team_stats
        self.team_id = team_id
        self.team_name = team_name,
        self.team_photo_url = team_photo_url

    def set_winning_matchups(self, winning_matchup):
        self.winning_matchup = winning_matchup
        self.winning_matchup_count = len(winning_matchup)

    

FullData = Blueprint("FullData", __name__)

cors = CORS(FullData)

def build_stat_obj(stat_array: list, stat_map: dict) -> dict:
    stats = {}
    for stat in stat_array:
        stat_id = stat["stat"]["stat_id"]

        if stat_id in stat_map:
            category_key = stat_map[stat_id]
            stat_value = stat["stat"]["value"]
            stats[category_key] = stat_value

    return stats

def compare_stats(team_stats: TeamStats, team_stats_compare: TeamStats, team_name: str) -> WinningMatchup:
    team_stats_dict = team_stats.__dict__
    team_stats_compare_dict = team_stats_compare.__dict__

    winning = [k for k in team_stats_dict if float(team_stats_dict[k]) > float(team_stats_compare_dict[k]) and k != "TO"]
    if team_stats_dict["TO"] < team_stats_compare_dict["TO"]:
        winning.append("TO")
    if len(winning) > 4:
        return WinningMatchup(team_name, winning)
    return None

# GET Returns current week team stats by category
# POST Returns week by week number passed
@FullData.route("/full-team-data-2", methods=["GET"])
@cross_origin()
def test2():
    full_matchup_information = lg.matchups()

    matchups = full_matchup_information["fantasy_content"]["league"][1]["scoreboard"]["0"]["matchups"]

    res = {}
    for x in range(0, int(matchups["count"])):
        team1 = matchups[str(x)]["matchup"]["0"]["teams"]["0"]["team"]
        team2 = matchups[str(x)]["matchup"]["0"]["teams"]["1"]["team"]
        team1stats = team1[1]["team_stats"]["stats"]
        team2stats = team2[1]["team_stats"]["stats"]

        team1stats = TeamStats(**build_stat_obj(team1stats, stat_map))
        team2stats = TeamStats(**build_stat_obj(team2stats, stat_map))

        team1Obj = Team(team1stats, team1[0][0]["team_key"], team1[0][2]["name"], team1[0][5]["team_logos"][0]["team_logo"]["url"])
        team2Obj = Team(team2stats, team2[0][0]["team_key"], team2[0][2]["name"], team2[0][5]["team_logos"][0]["team_logo"]["url"])

        res[team1[0][0]["team_key"]] = team1Obj
        res[team2[0][0]["team_key"]] = team2Obj

    print(res)

    for team in res:
        winning_matchups = []
        for team_compare in res:
            if team == team_compare:
                continue
            print(res[team].team_name, res[team_compare].team_name)
            matchup_won = compare_stats(res[team].team_stats, res[team_compare].team_stats, res[team_compare].team_name)
            if matchup_won is not None:
                winning_matchups.append(matchup_won)
        
        res[team].set_winning_matchups(winning_matchups)


    return jsonify("")

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


