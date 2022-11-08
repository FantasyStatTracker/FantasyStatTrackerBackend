import logging
from flask import Blueprint
from flask_cors import cross_origin
from HelperMethods.helper import get_team_map
from Variables.TokenRefresh import lg
from Model.variable import MatchupHistory

Api = Blueprint("Api", __name__)

# todo: Needs a lot of work
@Api.route("/streak", methods=["GET"])  # winning
@cross_origin()
def update_roster_stats():
    return ""
