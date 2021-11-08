from flask import Blueprint, jsonify, request
import requests
from flask_cors import cross_origin
from Variables.TokenRefresh import oauth, lg, apiKey
from pytz import timezone
import json
import datetime

RelevantData = Blueprint('RelevantData', __name__)

from Model.variable import Variable, db
year = "2021"
PlayerList = []

#Get all data for current season
@RelevantData.route('/full-player-data', methods=['GET']) #run once per year
@cross_origin()
def getFullPlayerData():
    headers = request.headers
    auth = headers.get("X-Api-Key")

    if (auth == apiKey):
        r  = requests.get('https://data.nba.net/10s/prod/v1/'+ year +'/players.json')
    else:
        return jsonify({"message":"ERROR: unauthorized"}), 401
    return r.json()


@RelevantData.route('/time-to-update', methods=['GET'])
def timeToUpdate():
    global PlayerList

    if (isinstance(PlayerList, list)):
        
        PlayerList = Variable.query.filter_by(variable_name="CurrentRoster").first()
    return str(int((1800 - abs(PlayerList.updated_at - datetime.datetime.now()).total_seconds())/60))


@RelevantData.route('/team-player-data', methods=['GET']) #run once per week maybe more
def lastWeekRoster(): #Over 10x faster because of list comprehension
    
    if not oauth.token_is_valid():
        oauth.refresh_access_token()

    # roster
    roster = {}

    for team in lg.teams():

        roster[team] = []
        
        est = timezone('EST')
        item = lg.player_stats([x["player_id"] for x in lg.to_team(team).roster()], 'lastweek', 2021)
        status = [y["status"] for y in lg.to_team(team).roster()]

        for x, y in zip(item, status):
            x["status"] = y

        roster[team]=item
    

    PredictionRoster = Variable.query.filter_by(variable_name="PredictionStats").first()
    PredictionRoster.variable_data = json.dumps(roster)
    db.session.commit()

    return roster

'''
@RelevantData.route('/tcum', methods=['GET']) #run once per week maybe more
def lastWeekRosterrr(): #Over 10x faster because of list comprehension
    average = ["PTS", "AST",
               "3PTM", "ST", "BLK", "TO", "REB"]
    
    #SeasonStat = lastWeekRosterr()
    #Prediction = Variable.query.filter_by(variable_name="StatCumulative").first()
    #StatCumulate = Prediction.variable_data

    
    for team1, team2 in zip(Week1, Week2):
        for player1, addToPlayer2 in zip(sorted(Week1[team1], key=lambda d: d["name"]), sorted(Week2[team2], key=lambda d: d["name"])):
            print(player1)
            for cat in average:
                
                try:
                    
                    if (player1["name"] == "Ricky Rubio"):
                        print("helrgsjkg")
                        
                    if (player1[cat] == '-'):
                        player1[cat] = 0.0
                    if (addToPlayer2[cat] == '-'):
                        addToPlayer2[cat] = 0.0
                    player1[cat] += addToPlayer2[cat]
                except:
                    print("hello")
                    continue
                
    return Week1
'''
