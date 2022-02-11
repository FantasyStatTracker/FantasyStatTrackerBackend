from Variables.TokenRefresh import lg
from collections import OrderedDict
import json
import requests
from Model.variable import Variable, db

def getFGFT():

    matchupInfo = lg.matchups(lg.current_week()-1)
    data = matchupInfo["fantasy_content"]["league"][1]["scoreboard"]["0"]["matchups"]
    matchupKey = list(data.keys())
    matchupKey = matchupKey[:-1]

    teamFGFT = {}
    tempVar = ""
    for matchupIndex in matchupKey:
        # matchup will always have two people
        for matchupIndividualTeam in range(0, 2):
            for TeamData in data[matchupIndex]["matchup"]["0"]["teams"][str(matchupIndividualTeam)]["team"]:
                try:

                    tempVar = TeamData[0]['team_key']
                except:
                    try:
                        teamFGFT[tempVar] = [
                            convert_to_float(
                                TeamData["team_stats"]["stats"][0]['stat']['value']),
                            convert_to_float(
                                TeamData["team_stats"]["stats"][2]['stat']['value'])
                        ]

                    except:
                        continue
    

    return teamFGFT

def convert_to_float(frac_str):
    try:
        return float(frac_str)
    except ValueError:
        num, denom = frac_str.split('/')
        try:
            leading, num = num.split(' ')
            whole = float(leading)
        except ValueError:
            whole = 0
        frac = float(num) / float(denom)
        return whole - frac if whole < 0 else whole + frac



def getTeamMap():

    matchupInfo = lg.matchups()
    teams = OrderedDict()
    data = matchupInfo["fantasy_content"]["league"][1]["scoreboard"]["0"]["matchups"]
    matchupKey = list(data.keys())
    matchupKey = matchupKey[:-1]

    teamMap = {}
    teamFGFT = {}
    current = ""
    for matchupIndex in matchupKey:
        # matchup will always have two people
        for matchupIndividualTeam in range(0, 2):
            for TeamData in data[matchupIndex]["matchup"]["0"]["teams"][str(matchupIndividualTeam)]["team"]:
                try:

                    teamMap[TeamData[0]['team_key']] = TeamData[2]['name']
                except:

                    continue
 

    return teamMap

def getSchedule():
    r = requests.get(
        'https://data.nba.com/data/10s/v2015/json/mobile_teams/nba/' + year + '/league/00_full_schedule.json')

    Game = {}
    data = r.json()

    for x in data['lscd']:
        Game[x["mscd"]["mon"]] = {}

        for y in x["mscd"]["g"]:
            Game[x["mscd"]["mon"]][y["gdte"]] = []
        for y in x["mscd"]["g"]:
            Game[x["mscd"]["mon"]][y["gdte"]].append(
                (y["v"]["ta"], y["h"]["ta"]))


    with open('./Variables/Schedule2021.py', 'w') as fo:
        fo.write("Sched =" + json.dumps(Game))
        fo.close
    return Game

def getMatchups(): #predict

    matchupInfo = lg.matchups()
    teams = OrderedDict()
    data = matchupInfo["fantasy_content"]["league"][1]["scoreboard"]["0"]["matchups"]
    matchupKey = list(data.keys())
    matchupKey = matchupKey[:-1]

    P1 = ""
    Matchup = {}
    current = ""
    for matchupIndex in matchupKey:
        # matchup will always have two people
        for matchupIndividualTeam in range(0, 2):
            for index, TeamData in enumerate(data[matchupIndex]["matchup"]["0"]["teams"][str(matchupIndividualTeam)]["team"]):

                try:

                    if (matchupIndividualTeam == 0):
                        P1 = TeamData[0]['team_key']
                    else:
                        Matchup[P1] = TeamData[0]['team_key']
                except:
                    continue


    Prediction = Variable.query.filter_by(variable_name="WeekMatchup").first()
    Prediction.variable_data=json.dumps(Matchup)
    db.session.commit()
        
    return Matchup

def dataCatReset():
    dataCats = {
    'Rk': None, 
    'Player':None,
    'Pos': None, 
    'Age': None, 
    'Tm': None, 
    'G': None, 
    'GS': None, 
    'MP': None, 
    'FG': None, 
    'FGA': None, 
    'FG%': None, 
    '3P': None, 
    '3PA': None, 
    '3P%': None, 
    '2P': None, 
    '2PA': None, 
    '2P%': None, 
    'eFG%': None, 
    'FT': None, 
    'FTA': None, 
    'FT%': None, 
    'ORB': None, 
    'DRB': None, 
    'TRB': None, 
    'AST': None, 
    'STL': None, 
    'BLK': None, 
    'TOV': None, 
    'PF': None, 
    'PTS': None}
    return dataCats