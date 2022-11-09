from flask import Blueprint, jsonify, request
import requests
from flask_cors import cross_origin
from Variables.TokenRefresh import api_key
import os

RelevantData = Blueprint("RelevantData", __name__)


year = os.environ.get("YEAR")
PLAYERLIST = []

# Get all data for current season


@RelevantData.route("/full-player-data", methods=["GET"])  # run once per year
@cross_origin()
def get_full_player_data():
    headers = request.headers
    auth = headers.get("X-Api-Key")

    if auth == api_key:
        r = requests.get("https://data.nba.net/10s/prod/v1/" + year + "/players.json")
    else:
        return jsonify({"message": "ERROR: unauthorized"}), 401
    return r.json()
