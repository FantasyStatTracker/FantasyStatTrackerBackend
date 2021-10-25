from flask import Blueprint, render_template, jsonify
import yahoo_fantasy_api as yfa
from yahoo_oauth import OAuth2
from Variables.TokenRefresh import oauth, gm, lg

from collections import OrderedDict


#Nothing
test_blueprint = Blueprint('test', __name__)



@test_blueprint.route('/roster', methods=['GET'])
def roster():
    tm = lg.to_team('410.l.136431.t.2')
    
    return jsonify(tm.roster())


#Sample full output
@test_blueprint.route('/full', methods=['POST']) 
def getAll():
    return lg.matchups()

#Sample player stats
@test_blueprint.route('/last', methods=['POST']) #test
def getLastWeek():
    return jsonify(lg.player_stats(6030, 'lastweek'))

    


