
from flask import Blueprint, request, jsonify
from flask_cors import  cross_origin
import json
from Variables.TokenRefresh import oauth, lg, apiKey
from .FullData import test
from .WinningMatchup import winning, getWins

Admin_Blueprint = Blueprint('Admin', __name__)

from Model.variable import MatchupHistory, db


@Admin_Blueprint.route('/updatePreviousWeek', methods=['GET']) #winning 
@cross_origin()
def updateRosterStats():
    headers = request.headers
    auth = headers.get("X-Api-Key")

    if (auth == apiKey):
        previousWeek = lg.current_week()-1

        previousWeekData = test(previousWeek).get_data()
        
        previousWinningMatchups = winning(previousWeekData).get_data().decode('utf-8')
        previousLeaders = getWins(previousWeekData).get_data().decode('utf-8')
        previousWeekData = previousWeekData.decode('utf-8')
        previousWeekData = json.loads(previousWeekData)["TeamData"]

        matchupRecord = MatchupHistory(
            matchup_week=previousWeek, 
            all_data=json.dumps(previousWeekData), 
            winning_matchup=previousWinningMatchups, 
            leader=previousLeaders
        )
        db.session.add(matchupRecord)
        db.session.commit()

    else:
        return jsonify({"message":"ERROR: unauthorized"}), 401

    
    return "Update Complete"