from flask import Blueprint, render_template, jsonify
import yahoo_fantasy_api as yfa
from yahoo_oauth import OAuth2
from Variables.TokenRefresh import oauth, gm, lg




#Nothing
test_blueprint = Blueprint('test', __name__)
@test_blueprint.route('/')
def index():
    return ""

#Sample full output
@test_blueprint.route('/full', methods=['POST']) 
def getAll():
    return lg.matchups()

#Sample player stats
@test_blueprint.route('/last', methods=['POST']) #test
def getLastWeek():
    return jsonify(lg.player_stats(6030, 'lastweek'))

    '''
@test_blueprint.route('/playoff', methods=['GET']) #what?
@cross_origin()
def playoff():
    oauth = OAuth2(None, None, from_file='oauth2.json')

    if not oauth.token_is_valid():
        oauth.refresh_access_token()

    teams = OrderedDict()

    matchupInfo = lg.matchups()

    # roster
    info = {}
    roster = {}
    league = {}

    for x in lg.teams():

        roster[x] = []

        for y in lg.to_team(x).roster():

            item = lg.player_stats(y["player_id"], 'lastweek')
            item.append(lg.player_details(y["player_id"])[
                        0]["editorial_team_abbr"])
            roster[x].append(item)

    return roster
'''
