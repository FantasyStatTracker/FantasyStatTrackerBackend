from flask import Blueprint
from flask_cors import cross_origin

Api = Blueprint("Api", __name__)

# todo: Needs a lot of work


@Api.route("/streak", methods=["GET"])  # winning
@cross_origin()
def update_roster_stats():
    return ""
