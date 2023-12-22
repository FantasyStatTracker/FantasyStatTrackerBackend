from flask import Blueprint, jsonify, Response, make_response
from flask_cors import cross_origin
from Variables.TokenRefresh import db
from bson import json_util, decode_all

Api = Blueprint("Api", __name__)
# todo: Needs a lot of work


@Api.route("/streak", methods=["GET"])  # winning
@cross_origin()
def update_roster_stats():
    data = db.companies.find()
    print(data)
    res = []
    # define data model for mongo outside of this and use that to make responses
    for field in data:
        g = {
            "_id": str(field["_id"]),
            "name": field["name"],
            "permalink": field["permalink"],
            "homepage_url": field["homepage_url"],
        }
        res.append(g)

    return jsonify(res)

