from flask import Blueprint, jsonify, request
from routes.RelevantData import lastWeekRoster
from Variables.Schedule2021 import *
from flask_cors import CORS
from Variables.TokenRefresh import oauth, lg
from pytz import timezone
import datetime
import json
from sqlalchemy import text
from HelperMethods.helper import getFGFT, getTeamMap

Prediction_Blueprint = Blueprint('Prediction', __name__)
cors = CORS(Prediction_Blueprint)

from Model.variable import Variable, PredictionHistory, db

TeamMap = []
PlayerList = []


@Prediction_Blueprint.route('/prediction-fast', methods=['GET']) #prediction
def predictionFast():
    
    Prediction = Variable.query.filter_by(variable_name="CurrentPrediction").first()
    sqlQuery = text("select extract(dow from (SELECT updated_at from variable where variable_name='CurrentPrediction'))")
    res = db.engine.execute(sqlQuery)
    day = 0
    for x in res:
        for y,z in x.items():
            day = z
            break
        break
    

    est = timezone('EST')
    if (day == 1.0 and (abs(Prediction.updated_at - datetime.now(est)).total_seconds()/60) > 1500):
        x = predict()
        Prediction = Variable.query.filter_by(variable_name="CurrentPrediction").first()
        Prediction.variable_data = x

        db.session.commit()
    

    return jsonify(Prediction.variable_data)

#Prediction Function
def predict():
    global TeamMap
    global PlayerList

    if not oauth.token_is_valid():
        oauth.refresh_access_token()

    teams = lg.teams()

    StatPrediction = {}
    

    if (isinstance(TeamMap, list)): #update team mapping iff there was a change (10x faster)
        TeamMap = Variable.query.filter_by(variable_name="TeamMap").first()

    if (isinstance(PlayerList, list)):
        PlayerList = Variable.query.filter_by(variable_name="PredictionStats").first()

    FGFT = getFGFT()

    #Populate Data
    for team in teams:
        predictionData = {"PTS": 0.0, "FG%": 0.0, "AST": 0.0, "FT%": 0.0,
            "3PTM": 0.0, "ST": 0.0, "BLK": 0.0, "TO": 0.0, "REB": 0.0}

        for player in PlayerList[team]:

            
            for x in predictionData.keys():
                try:
                    if (player['status'] == 'INJ'):
                        continue
                    predictionData[x] += player[x]
                except:
                    continue

            try:
                predictionData["FG%"] = float(FGFT[team][0])
                predictionData["FT%"] = float(FGFT[team][1])
            except:
                continue

        StatPrediction[team] = predictionData

    matchUp = Variable.query.filter_by(variable_name="WeekMatchup").first().variable_data

    
    PredictionArray = []

    #Compare Populated Data to Find Winner
    for team in matchUp:
        opponent = matchUp[team]
        Prediction = {team: 0, opponent: 0}
        for cat1 in StatPrediction[team]:
            if (cat1 == 'TO'):
                if (StatPrediction[team][cat1] < StatPrediction[opponent][cat1]):
                    Prediction[team] += 1
                elif (StatPrediction[team][cat1] > StatPrediction[opponent][cat1]):
                    Prediction[opponent] += 1
                else:
                    continue
                continue

            if (StatPrediction[team][cat1] > StatPrediction[opponent][cat1]):
                Prediction[team] += 1
            elif (StatPrediction[team][cat1] < StatPrediction[opponent][cat1]):
                Prediction[opponent] += 1
            else:
                continue

        PredictionArray.append(Prediction)

    for x in StatPrediction:
        StatPrediction[x]['FG%'] = round(StatPrediction[x]['FG%'], 3)
        StatPrediction[x]['FT%'] = round(StatPrediction[x]['FT%'], 3)

    ReturnPrediction = []

    for x in PredictionArray:
        newDict = {}
        for match in x.keys():
            newDict[TeamMap.variable_data[match]] = [x[match], StatPrediction[match]]
        ReturnPrediction.append(newDict)

    
    try:
        item = Variable.query.filter_by(variable_name="CurrentPrediction").first()
        item.variable_data=json.dumps(ReturnPrediction)
        item.updated_at=datetime.datetime.now()
        db.session.commit()
    except:
        print("Entry already exists")
    
    
    predictionItem = PredictionHistory(prediction_week=lg.current_week(), prediction_data=json.dumps(ReturnPrediction), prediction_correct=0)
    try:
        db.session.add(predictionItem)
        db.session.commit()
    except:
        print("Entry already Exists")
    
        

    return jsonify(ReturnPrediction)


#Returns Team FG% and FT% for the week


#returns top performers per team by category lead
@Prediction_Blueprint.route('/TopPerformers', methods=['POST'])
def getTopPerformers():

    
    global TeamMap
    global PlayerList

    
    data = json.loads(request.form.get("team"))
    categoryRanking = json.loads(request.form.get("categoryRanking"))
    TeamToFetch = ""

    
    if (isinstance(TeamMap, list)): #update team mapping iff there was a change (10x faster)
        TeamMap = Variable.query.filter_by(variable_name="TeamMap").first()

    if (data not in TeamMap.variable_data.values()):
        newTeamMap = getTeamMap()
        TeamMap = Variable.query.filter_by(variable_name="TeamMap").first()
        TeamMap.variable_data = json.dumps(newTeamMap)
        db.session.commit()        

    
    if (isinstance(PlayerList, list)):
        
        PlayerList = Variable.query.filter_by(variable_name="CurrentRoster").first()

    if (abs(PlayerList.updated_at - datetime.datetime.now()).total_seconds()) > 1800:

        newRoster = lastWeekRoster()
        PlayerList.variable_data = json.dumps(newRoster)
        PlayerList.updated_at = datetime.datetime.now()
        db.session.commit()

        PlayerList = Variable.query.filter_by(variable_name="CurrentRoster").first()
        
    
    
    for x in TeamMap.variable_data:
        if (TeamMap.variable_data[x] == data):
            TeamToFetch = x
            break

    
    MaxCat = {}

    
    MaxCat = dict.fromkeys(categoryRanking, {"Value": 0.0, "PlayerFirst": "", "PlayerLast": ""})
    for Player in PlayerList.variable_data[TeamToFetch]:

            
            for individualCategory in categoryRanking:
                
                if (Player[individualCategory] == '-'):
                    Player[individualCategory] = 0.0
                    
                if (MaxCat[individualCategory]["Value"] <= float(Player[individualCategory])):
                    Name = Player["name"].split()
                    if (Name[0] == "Robert" and Name[1] == "Williams"):
                        Name[1] = "Williams III"
                    
                    MaxCat[individualCategory] = {"Value": float(Player[individualCategory]), 
                                                        "PlayerFirst": Name[0],
                                                        "PlayerLast": ' '.join(Name[x] for x in range(1,len(Name)))
                                                }
                    
    delete = []
    for key in MaxCat:
        if (MaxCat[key]["PlayerFirst"] == ""):
            delete.append(key)


    for deletionKey in delete:
        del MaxCat[deletionKey]


    return jsonify(MaxCat)






