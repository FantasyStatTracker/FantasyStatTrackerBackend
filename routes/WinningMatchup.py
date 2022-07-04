from flask import Blueprint, request
from flask_cors import cross_origin
import json
from Variables.TokenRefresh import oauth
from .FullData import get_category

WinningMatchup_Blueprint = Blueprint("WinningMatchup", __name__)


@WinningMatchup_Blueprint.route(
    "/category-leader", methods=["POST"]
)  # Category Leaders
@cross_origin()
def get_wins(*args):

    dataset = None
    try:
        dataset = args[0]
    except:
        pass

    if not oauth.token_is_valid():
        oauth.refresh_access_token()

    if dataset == None:
        data = json.loads(request.form.get("data"))
    else:
        data = [json.loads(dataset)["TeamData"]]

    category_array = json.loads(get_category().data)
    category_max = {category: {} for category in category_array}

    for team_statistics in data:
        for team in list(team_statistics.keys()):  # team stats
            for category in category_array:  # cats
                try:
                    category_max[category][team] = float(
                        team_statistics[team][category]
                    )
                except:
                    category_max[category][team] = 0.0

    return category_max


@WinningMatchup_Blueprint.route(
    "/winning-matchups", methods=["POST"]
)  # Team vs. Other Teams
@cross_origin()
def winning(*args):

    dataset = None
    try:
        dataset = args[0]
    except:
        pass
    if dataset == None:
        data = json.loads(request.form.get("data"))
    else:
        data = [json.loads(dataset)["TeamData"]]

    print(data)
    current_wins = {}

    for x in data:
        print(x)
        for player1 in list(x.keys()):  # team stats
            current_wins[player1] = []
            for y in data:
                for player2 in list(y.keys()):

                    if player1 == player2:
                        continue

                    win_count = 0
                    loss_count = 0
                    category_wins = []

                    # different condition for Turnovers
                    if float(x[player1]["TO"]) < float(y[player2]["TO"]):
                        win_count += 1
                        category_wins.append("TO")
                    elif float(x[player1]["TO"]) == float(y[player2]["TO"]):
                        None
                    else:
                        loss_count += 1
                    for z in x[player1].keys():  # cats
                        if z == "TO":
                            continue
                        comp = float(x[player1][z]) > float(y[player2][z])
                        if comp:  # check how many wins
                            win_count += 1
                            category_wins.append(z)
                        elif float(x[player1][z]) == float(y[player2][z]):
                            continue
                        else:
                            loss_count += 1

                    if win_count > loss_count:
                        current_wins[player1].append({player2: category_wins})

    return current_wins  # json object with Team { Wins { Categorieswon


"""
@WinningMatchup_Blueprint.route('/winning-matchups', methods=['POST']) #Team vs. Other Teams
@cross_origin()
def winnings(*args):

    dataset = None
    try:
        dataset = args[0]
    except:
        pass
    if (dataset == None):
        data = json.loads(request.form.get("data"))
    else:
        data = [json.loads(dataset)["TeamData"]]

    current_wins = {}

    for allData in data:
        for player1 in list(allData.keys()):  # team stats
            current_wins[player1] = []

            for player2 in list(allData.keys()):

                if (player1 == player2):
                    continue

                win_count = 0
                category_wins = []

                # different condition for Turnovers
                if (float(allData[player1]['TO']) < float(allData[player2]['TO'])):
                    win_count += 1
                    category_wins.append('TO')
                for category in allData[player1].keys():  # cats

                    comparisonResult = float(allData[player1][category]) > float(allData[player2][category])
                    if (comparisonResult and category != 'TO'):  # check how many wins
                        win_count += 1
                        category_wins.append(category)

                if (win_count >= 5):
                    current_wins[player1].append({player2: category_wins})

    return current_wins  # json object with Team { Wins { Categorieswon

"""

