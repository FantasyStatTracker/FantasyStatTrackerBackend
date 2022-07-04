from flask import Blueprint
from flask_cors import CORS
from bs4 import BeautifulSoup
from HelperMethods.helper import dataCatReset
from statistics import stdev
import requests
import scipy.stats as stats

PlayerStatisticsBlueprint = Blueprint("PlayerStatistics", __name__)
cors = CORS(PlayerStatisticsBlueprint)


@PlayerStatisticsBlueprint.route("/player_zscore", methods=["GET"])
def player_zscore():

    url = "https://www.basketball-reference.com/leagues/NBA_2022_per_game.html"

    response = requests.get(url)

    html = response.text

    soup = BeautifulSoup(response.content, "lxml")

    x = soup.find("table", {"id": "per_game_stats"})
    full_player_data_bbref = {}

    rows = x.findChildren(["tr"])

    counter = 0
    for row in rows:
        j = row.get_text(separator=",", strip=True)
        player_array = j.split(",")

        data_category_dict = dataCatReset()

        if player_array[0] != "Rk":

            if len(player_array) != len(data_category_dict):
                player_array.insert(8, "0.0")
            for x, y in zip(player_array, data_category_dict):

                data_category_dict[y] = x

            if int(data_category_dict["G"]) < 37:
                continue
            full_player_data_bbref[
                str(player_array[1] + "-" + player_array[4])
            ] = data_category_dict

    totals = dataCatReset()
    for x in totals:
        totals[x] = 0.0
    for x in full_player_data_bbref:
        for z, y in zip(totals, full_player_data_bbref[x]):
            try:
                totals[z] += float(full_player_data_bbref[x][y])
            except:
                continue

    for x in totals:
        try:
            totals[x] /= len(full_player_data_bbref)
        except:
            continue

    league_average = totals

    standard_dev = dataCatReset()
    z_score = dataCatReset()

    for x in standard_dev:
        standard_dev[x] = []

    for x in full_player_data_bbref:
        for z, y in zip(standard_dev, full_player_data_bbref[x]):
            try:
                standard_dev[z].append(float(full_player_data_bbref[x][y]))
            except:
                continue

    for x in standard_dev:
        try:
            standard_deviation = stdev(standard_dev[x])
            z_score[x] = stats.zscore(standard_dev[x])
            standard_dev[x] = standard_deviation
        except:
            continue

    def ZScore(val, mean, stdev):
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
                z_score_data[x][y] = ZScore(
                    float(full_player_data_bbref[x][y]),
                    float(league_average[y]),
                    float(standard_dev[y]),
                )
            except:
                continue

    z_score_data["league_average"] = league_average
    return z_score_data
