import logging
from Variables.TokenRefresh import lg
import json
import requests
from Model.variable import Variable, db


def get_FG_FT():

    matchup_information = lg.matchups(lg.current_week() - 1)
    data = matchup_information["fantasy_content"]["league"][1]["scoreboard"]["0"][
        "matchups"
    ]
    matchup_key = list(data.keys())
    matchup_key = matchup_key[:-1]

    team_FG_FT = {}
    team_key = ""
    for matchup_index in matchup_key:
        # matchup will always have two people
        for matchup_team in range(0, 2):
            for team_data in data[matchup_index]["matchup"]["0"]["teams"][
                str(matchup_team)
            ]["team"]:
                try:

                    team_key = team_data[0]["team_key"]
                except Exception as e:
                    logging.info(
                        "Alternate Calculation, {e}".format(e=e.__class__.__name__)
                    )
                    try:
                        team_FG_FT[team_key] = [
                            convert_to_float(
                                team_data["team_stats"]["stats"][0]["stat"]["value"]
                            ),
                            convert_to_float(
                                team_data["team_stats"]["stats"][2]["stat"]["value"]
                            ),
                        ]

                    except Exception as e:
                        logging.exception(e.__class__.__name__)
                        continue

    return team_FG_FT


def convert_to_float(frac_str):
    try:
        return float(frac_str)
    except ValueError:
        num, denom = frac_str.split("/")
        try:
            leading, num = num.split(" ")
            whole = float(leading)
        except ValueError:
            whole = 0
        frac = float(num) / float(denom)
        return whole - frac if whole < 0 else whole + frac


def get_team_map():

    matchup_information = lg.matchups()
    data = matchup_information["fantasy_content"]["league"][1]["scoreboard"]["0"][
        "matchups"
    ]
    matchup_key = list(data.keys())
    matchup_key = matchup_key[:-1]

    team_map = {}
    for matchup_index in matchup_key:
        # matchup will always have two people
        for matchup_team in range(0, 2):
            for team_data in data[matchup_index]["matchup"]["0"]["teams"][
                str(matchup_team)
            ]["team"]:
                try:
                    team_map[team_data[0]["team_key"]] = team_data[2]["name"]
                except Exception as e:
                    logging.exception(e.__class__.__name__)
                    continue

    return team_map


def get_team_id_to_name_map():
    map = get_team_map()
    inv_map = {v: k for k, v in map.items()}
    return inv_map


def get_schedule():
    year = "2021"
    r = requests.get(
        f"https://data.nba.com/data/10s/v2015/json/mobile_teams/nba/{year}/league/00_full_schedule.json"
    )
    Game = {}
    data = r.json()

    for x in data["lscd"]:
        Game[x["mscd"]["mon"]] = {}

        for y in x["mscd"]["g"]:
            Game[x["mscd"]["mon"]][y["gdte"]] = []
        for y in x["mscd"]["g"]:
            Game[x["mscd"]["mon"]][y["gdte"]].append((y["v"]["ta"], y["h"]["ta"]))

    with open("./Variables/Schedule2021.py", "w") as fo:
        fo.write("Sched =" + json.dumps(Game))
        fo.close
    return Game


def get_league_matchups():  # predict

    matchup_information = lg.matchups()
    data = matchup_information["fantasy_content"]["league"][1]["scoreboard"]["0"][
        "matchups"
    ]
    matchup_key = list(data.keys())
    matchup_key = matchup_key[:-1]

    P1 = ""
    Matchup = {}
    for matchup_index in matchup_key:
        # matchup will always have two people
        for matchup_team in range(0, 2):
            for _, team_data in enumerate(
                data[matchup_index]["matchup"]["0"]["teams"][str(matchup_team)]["team"]
            ):

                try:

                    if matchup_team == 0:
                        P1 = team_data[0]["team_key"]
                    else:
                        Matchup[P1] = team_data[0]["team_key"]
                except Exception as e:
                    logging.info(e.__class__.__name__)
                    continue

    Prediction = Variable.query.filter_by(variable_name="WeekMatchup").first()
    Prediction.variable_data = json.dumps(Matchup)
    db.session.commit()

    return Matchup


def get_data_category_map():
    data_category_map = {
        "Rk": None,
        "Player": None,
        "Pos": None,
        "Age": None,
        "Tm": None,
        "G": None,
        "GS": None,
        "MP": None,
        "FG": None,
        "FGA": None,
        "FG%": None,
        "3P": None,
        "3PA": None,
        "3P%": None,
        "2P": None,
        "2PA": None,
        "2P%": None,
        "eFG%": None,
        "FT": None,
        "FTA": None,
        "FT%": None,
        "ORB": None,
        "DRB": None,
        "TRB": None,
        "AST": None,
        "STL": None,
        "BLK": None,
        "TOV": None,
        "PF": None,
        "PTS": None,
    }
    return data_category_map


# gm is a yfa Game
def get_team_id(gm):

    return gm.league_ids()


def convert_previous_week_data(previous_week_data):
    team_map = get_team_id_to_name_map()

    for x in list(previous_week_data.keys()):
        previous_week_data[team_map[x]] = previous_week_data[x]
        del previous_week_data[x]

    return previous_week_data
