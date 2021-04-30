from flask import Blueprint, render_template, jsonify, request
import yahoo_fantasy_api as yfa
from yahoo_oauth import OAuth2
from collections import OrderedDict
from flask_cors import CORS, cross_origin
from operator import itemgetter
import json
from Variables.TokenRefresh import token


data = token()

oauth = data["oauth"]
gm = data["gm"]
lg = data["lg"]

WinningMatchup_Blueprint = Blueprint('WinningMatchup', __name__)


@WinningMatchup_Blueprint.route('/win-calculator', methods=['POST']) #win calc
@cross_origin()
def getWins():

    if not oauth.token_is_valid():
        oauth.refresh_access_token()

    data = json.loads(request.form.get("data"))
    categoryMax = {"FG%": {}, "FT%": {}, "3PTM": {}, "PTS": {},
                   "REB": {}, "AST": {}, "ST": {}, "BLK": {}, "TO": {}}

    for x in data:

        for y in list(x.keys()):  # team stats

            for z in x[y].keys():  # cats
                try:
                    categoryMax[z][y] = float(x[y][z])
                except:
                    categoryMax[z][y] = 0

    catSort = {}
    for x in categoryMax:
        sortedCategory = (
            sorted(categoryMax[x].items(), key=itemgetter(1), reverse=True))
        catSort[x] = sortedCategory

    return catSort



@WinningMatchup_Blueprint.route('/winning-matchups', methods=['POST']) #winning 
@cross_origin()
def winning():
    data = json.loads(request.form.get("data"))
    currentWins = {}

    for x in data:
        for player1 in list(x.keys()):  # team stats
            currentWins[player1] = []
            for y in data:
                for player2 in list(y.keys()):

                    if (player1 == player2):
                        continue

                    winCount = 0
                    catWins = []

                    # different condition for Turnovers
                    if (float(x[player1]['TO']) < float(y[player2]['TO'])):
                        winCount += 1
                        catWins.append('TO')
                    for z in x[player1].keys():  # cats

                        comp = float(x[player1][z]) > float(y[player2][z])
                        if (comp and z != 'TO'):  # check how many wins
                            winCount += 1
                            catWins.append(z)

                    if (winCount >= 5):
                        currentWins[player1].append({player2: catWins})

    return currentWins  # json object with Team { Wins { Categorieswon