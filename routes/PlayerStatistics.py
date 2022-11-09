import logging
from flask import Blueprint
from flask_cors import CORS
from bs4 import BeautifulSoup
from HelperMethods.helper import get_data_category_map
from statistics import stdev
from cache import cache
import requests
import os
import scipy.stats as stats

PlayerStatistics = Blueprint("PlayerStatistics", __name__)
cors = CORS(PlayerStatistics)
year = os.environ.get("YEAR")


@PlayerStatistics.route("/player-zscore", methods=["GET"])
@cache.cached()
def player_zscore():

    url = os.environ.get("URL")

    response = requests.get(url)

    soup = BeautifulSoup(response.content, "lxml")

    x = soup.find("table", {"id": "per_game_stats"})
    full_player_data_bbref = {}

    rows = x.findChildren(["tr"])

    for row in rows:
        j = row.get_text(separator=",", strip=True)
        player_array = j.split(",")

        data_category_dict = get_data_category_map()

        if player_array[0] != "Rk":

            if len(player_array) != len(data_category_dict):
                player_array.insert(8, "0.0")
            for x, y in zip(player_array, data_category_dict):

                data_category_dict[y] = x

            """
            if int(data_category_dict["G"]) < 37:
                continue
            """
            full_player_data_bbref[
                str(player_array[1] + "-" + player_array[4])
            ] = data_category_dict

    totals = get_data_category_map()
    for x in totals:
        totals[x] = 0.0
    for x in full_player_data_bbref:
        for z, y in zip(totals, full_player_data_bbref[x]):
            try:
                totals[z] += float(full_player_data_bbref[x][y])
            except Exception as e:
                logging.exception(e.__class__.__name__)
                continue

    for x in totals:
        try:
            totals[x] /= len(full_player_data_bbref)
        except Exception as e:
            logging.exception(e.__class__.__name__)
            continue

    league_average = totals

    standard_dev = get_data_category_map()
    z_score = get_data_category_map()

    for x in standard_dev:
        standard_dev[x] = []

    for x in full_player_data_bbref:
        for z, y in zip(standard_dev, full_player_data_bbref[x]):
            try:
                standard_dev[z].append(float(full_player_data_bbref[x][y]))
            except Exception as e:
                logging.exception(e.__class__.__name__)
                continue

    for x in standard_dev:
        try:
            standard_deviation = stdev(standard_dev[x])
            z_score[x] = stats.zscore(standard_dev[x])
            standard_dev[x] = standard_deviation
        except Exception as e:
            logging.exception(e.__class__.__name__)
            continue

    def calculate_zscore(val, mean, stdev):
        return round((val - mean) / stdev, 2)

    relevant_cat = [
        "FG%",
        "FT%",
        "3P",
        "PTS",
        "TRB",
        "AST",
        "STL",
        "BLK",
        "TOV",
        "Player",
    ]
    z_score_data = full_player_data_bbref
    for x in full_player_data_bbref:
        for y in full_player_data_bbref[x]:
            if y not in relevant_cat:
                z_score_data[x][y] = ""
                continue
            try:
                z_score_data[x][y] = calculate_zscore(
                    float(full_player_data_bbref[x][y]),
                    float(league_average[y]),
                    float(standard_dev[y]),
                )
            except Exception as e:
                logging.exception(e.__class__.__name__)
                continue

    z_score_data["league_average"] = league_average
    return z_score_data
