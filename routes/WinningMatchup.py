import logging
from flask import Blueprint, request
from flask_cors import cross_origin
import json
from Variables.TokenRefresh import oauth
from .FullData import get_category

WinningMatchup = Blueprint("WinningMatchup", __name__)


@WinningMatchup.route("/category-leader", methods=["POST"])  # Category Leaders
@cross_origin()
def get_wins(*args):

    dataset = None
    try:
        dataset = args[0]
    except Exception as e:
        logging.exception(e.__class__.__name__)
        pass

    if not oauth.token_is_valid():
        oauth.refresh_access_token()

    if dataset is None:
        team_statistics_data = json.loads(request.form.get("data"))
    else:
        team_statistics_data = [json.loads(dataset)["team_data"]]

    category_array = json.loads(get_category().data)
    category_max = {category: {} for category in category_array}

    for team_statistics in team_statistics_data:
        for team in team_statistics.keys():  # team stats
            for category in category_array:
                try:
                    category_max[category][team] = float(
                        team_statistics[team][category]
                    )
                except Exception as e:
                    logging.exception(e.__class__.__name__)
                    category_max[category][team] = 0.0

    return category_max


@WinningMatchup.route("/winning-matchups", methods=["POST"])  # Team vs. Other Teams
@cross_origin()
def winning(*args):

    dataset = None
    try:
        dataset = args[0]
    except Exception as e:
        logging.exception(e.__class__.__name__)
        pass
    if dataset is None:
        team_statistics_data = json.loads(request.form.get("data"))
    else:
        team_statistics_data = [json.loads(dataset)["team_data"]]

    current_wins = {}

    for team_statistics in team_statistics_data:
        for selected_team_1 in team_statistics.keys():  # team stats
            current_wins[selected_team_1] = []
            for team_statistics_compare in team_statistics_data:
                for selected_team_2 in team_statistics_compare.keys():

                    if selected_team_1 == selected_team_2:
                        continue

                    win_count = 0
                    loss_count = 0
                    category_wins = []

                    # different condition for Turnovers
                    if float(team_statistics[selected_team_1]["TO"]) < float(
                        team_statistics_compare[selected_team_2]["TO"]
                    ):
                        win_count += 1
                        category_wins.append("TO")
                    elif float(team_statistics[selected_team_1]["TO"]) == float(
                        team_statistics_compare[selected_team_2]["TO"]
                    ):
                        None
                    else:
                        loss_count += 1
                    for category in team_statistics[selected_team_1].keys():  # cats
                        if category == "TO":
                            continue
                        selected_team_win_boolean = float(
                            team_statistics[selected_team_1][category]
                        ) > float(team_statistics_compare[selected_team_2][category])
                        if selected_team_win_boolean:  # check how many wins
                            win_count += 1
                            category_wins.append(category)
                        elif float(team_statistics[selected_team_1][category]) == float(
                            team_statistics_compare[selected_team_2][category]
                        ):
                            continue
                        else:
                            loss_count += 1

                    if win_count > loss_count:
                        current_wins[selected_team_1].append(
                            {selected_team_2: category_wins}
                        )

    return current_wins  # json object with Team { Wins { Categorieswon
