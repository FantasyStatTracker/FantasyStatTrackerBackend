from flask import Blueprint, jsonify, request
import requests
from flask_cors import CORS
from HelperMethods.helper import get_team_map
from Variables.TokenRefresh import oauth, lg
from pytz import timezone
import json
import datetime
from Model.variable import Variable, db
from Variables.TokenRefresh import oauth, lg

TeamInformation = Blueprint("TeamInformation", __name__)
cors = CORS(TeamInformation)


@TeamInformation.route("/team-injury", methods=["GET"])
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
