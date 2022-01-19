
from collections import namedtuple
from tokenize import Name
from typing import Match
from flask import Blueprint, request, jsonify
from flask.signals import request_tearing_down
from flask_cors import  cross_origin
import json
import requests
from HelperMethods.helper import getTeamMap
from Variables.TokenRefresh import lg, apiKey
from .FullData import test
from .WinningMatchup import winning, getWins
from .RelevantData import lastWeekRoster
from  HelperMethods.helper import getMatchups
from .Prediction import TeamMap, predict
from basketball_reference_scraper.players import get_stats, get_game_logs, get_player_headshot



Api_Blueprint = Blueprint('Api', __name__)

from Model.variable import MatchupHistory, db


@Api_Blueprint.route('/streak', methods=['GET']) #winning 
@cross_origin()
def updateRosterStats():

    skipAll = True
    if (not skipAll):
        def editTeamName(name) -> str:
            if (name == 'Badedayo' or name == 'More Dead'):
                return 'Dead'
            elif (name == 'Bandemic P'):
                return 'Protocols P'
            elif (name == 'LeInjured' or name == 'LeStrain' or name == 'LeEjected' or name == 'LeCovid'):
                return 'LeAntiClutch'

            return name

        Matchup = {
        1: {
            'LeAntiClutch': 'Protocols P',
            'JKimothy': "Nathan's Phenomenal Team",
            'Protocols P': 'LeAntiClutch',
            'Team Goon Cena': "Sufyan's Superb Team",
            'Dead': "Samuel's Tip-Top Team",
            'Kentucky Jr.': 'gae young',
            'gae young': 'Kentucky Jr.',
            'Last Place Projected': "Liam's Squad of Goofy Goobers",
            "Liam's Squad of Goofy Goobers": 'Last Place Projected',
            "Nathan's Phenomenal Team": 'JKimothy',
            "Sufyan's Superb Team": 'Team Goon Cena',
            "Samuel's Tip-Top Team": 'Dead'
        },
        2: {
            'LeAntiClutch': "Nathan's Phenomenal Team",
            'JKimothy': 'Dead',
            'Protocols P': "Liam's Squad of Goofy Goobers",
            'Team Goon Cena': 'Last Place Projected',
            'Dead': 'JKimothy',
            'Kentucky Jr.': "Samuel's Tip-Top Team",
            'gae young': "Sufyan's Superb Team",
            'Last Place Projected': 'Team Goon Cena',
            "Liam's Squad of Goofy Goobers": 'Protocols P',
            "Nathan's Phenomenal Team": 'LeAntiClutch',
            "Sufyan's Superb Team": 'gae young',
            "Samuel's Tip-Top Team": 'Kentucky Jr.'
        },
        3: {
            'LeAntiClutch': 'JKimothy',
            'JKimothy': 'LeAntiClutch',
            'Protocols P': 'Team Goon Cena',
            'Team Goon Cena': 'Protocols P',
            'Dead': 'Kentucky Jr.',
            'Kentucky Jr.': 'Dead',
            'gae young': 'Last Place Projected',
            'Last Place Projected': 'gae young',
            "Liam's Squad of Goofy Goobers": "Nathan's Phenomenal Team",
            "Nathan's Phenomenal Team": "Liam's Squad of Goofy Goobers",
            "Sufyan's Superb Team": "Samuel's Tip-Top Team",
            "Samuel's Tip-Top Team": "Sufyan's Superb Team"
        },
        4: {
            'LeAntiClutch': "Liam's Squad of Goofy Goobers",
            'JKimothy': 'Kentucky Jr.',
            'Protocols P': 'gae young',
            'Team Goon Cena': "Nathan's Phenomenal Team",
            'Dead': "Sufyan's Superb Team",
            'Kentucky Jr.': 'JKimothy',
            'gae young': 'Protocols P',
            'Last Place Projected': "Samuel's Tip-Top Team",
            "Liam's Squad of Goofy Goobers": 'LeAntiClutch',
            "Nathan's Phenomenal Team": 'Team Goon Cena',
            "Sufyan's Superb Team": 'Dead',
            "Samuel's Tip-Top Team": 'Last Place Projected'
        },
        5: {
            'LeAntiClutch': 'Team Goon Cena',
            'JKimothy': "Liam's Squad of Goofy Goobers",
            'Protocols P': "Samuel's Tip-Top Team",
            'Team Goon Cena': 'LeAntiClutch',
            'Dead': 'Last Place Projected',
            'Kentucky Jr.': "Sufyan's Superb Team",
            'gae young': "Nathan's Phenomenal Team",
            'Last Place Projected': 'Dead',
            "Liam's Squad of Goofy Goobers": 'JKimothy',
            "Nathan's Phenomenal Team": 'gae young',
            "Sufyan's Superb Team": 'Kentucky Jr.',
            "Samuel's Tip-Top Team": 'Protocols P'
        },
        6: {
            'LeAntiClutch': 'gae young',
            'JKimothy': "Sufyan's Superb Team",
            'Protocols P': 'Dead',
            'Team Goon Cena': "Liam's Squad of Goofy Goobers",
            'Dead': 'Protocols P',
            'Kentucky Jr.': 'Last Place Projected',
            'gae young': 'LeAntiClutch',
            'Last Place Projected': 'Kentucky Jr.',
            "Liam's Squad of Goofy Goobers": 'Team Goon Cena',
            "Nathan's Phenomenal Team": "Samuel's Tip-Top Team",
            "Sufyan's Superb Team": 'JKimothy',
            "Samuel's Tip-Top Team": "Nathan's Phenomenal Team"
        },
        7: {
            'LeAntiClutch': "Samuel's Tip-Top Team",
            'JKimothy': 'Team Goon Cena',
            'Protocols P': 'Kentucky Jr.',
            'Team Goon Cena': 'JKimothy',
            'Dead': "Nathan's Phenomenal Team",
            'Kentucky Jr.': 'Protocols P',
            'gae young': "Liam's Squad of Goofy Goobers",
            'Last Place Projected': "Sufyan's Superb Team",
            "Liam's Squad of Goofy Goobers": 'gae young',
            "Nathan's Phenomenal Team": 'Dead',
            "Sufyan's Superb Team": 'Last Place Projected',
            "Samuel's Tip-Top Team": 'LeAntiClutch'
        },
        8: {
            'LeAntiClutch': 'Dead',
            'JKimothy': 'Last Place Projected',
            'Protocols P': "Sufyan's Superb Team",
            'Team Goon Cena': 'gae young',
            'Dead': 'LeAntiClutch',
            'Kentucky Jr.': "Nathan's Phenomenal Team",
            'gae young': 'Team Goon Cena',
            'Last Place Projected': 'JKimothy',
            "Liam's Squad of Goofy Goobers": "Samuel's Tip-Top Team",
            "Nathan's Phenomenal Team": 'Kentucky Jr.',
            "Sufyan's Superb Team": 'Protocols P',
            "Samuel's Tip-Top Team": "Liam's Squad of Goofy Goobers"
        },
        9: {
            'LeAntiClutch': 'Kentucky Jr.',
            'JKimothy': 'gae young',
            'Protocols P': 'Last Place Projected',
            'Team Goon Cena': "Samuel's Tip-Top Team",
            'Dead': "Liam's Squad of Goofy Goobers",
            'Kentucky Jr.': 'LeAntiClutch',
            'gae young': 'JKimothy',
            'Last Place Projected': 'Protocols P',
            "Liam's Squad of Goofy Goobers": 'Dead',
            "Nathan's Phenomenal Team": "Sufyan's Superb Team",
            "Sufyan's Superb Team": "Nathan's Phenomenal Team",
            "Samuel's Tip-Top Team": 'Team Goon Cena'
        },
        10: {
            'LeAntiClutch': "Sufyan's Superb Team",
            'JKimothy': 'Protocols P',
            'Protocols P': 'JKimothy',
            'Team Goon Cena': 'Dead',
            'Dead': 'Team Goon Cena',
            'Kentucky Jr.': "Liam's Squad of Goofy Goobers",
            'gae young': "Samuel's Tip-Top Team",
            'Last Place Projected': "Nathan's Phenomenal Team",
            "Liam's Squad of Goofy Goobers": 'Kentucky Jr.',
            "Nathan's Phenomenal Team": 'Last Place Projected',
            "Sufyan's Superb Team": 'LeAntiClutch',
            "Samuel's Tip-Top Team": 'gae young'
        },
        11: {
            'LeAntiClutch': 'Last Place Projected',
            'JKimothy': "Samuel's Tip-Top Team",
            'Protocols P': "Nathan's Phenomenal Team",
            'Team Goon Cena': 'Kentucky Jr.',
            'Dead': 'gae young',
            'Kentucky Jr.': 'Team Goon Cena',
            'gae young': 'Dead',
            'Last Place Projected': 'LeAntiClutch',
            "Liam's Squad of Goofy Goobers": "Sufyan's Superb Team",
            "Nathan's Phenomenal Team": 'Protocols P',
            "Sufyan's Superb Team": "Liam's Squad of Goofy Goobers",
            "Samuel's Tip-Top Team": 'JKimothy'
        },
        12: {
            'LeAntiClutch': 'Protocols P',
            'JKimothy': "Nathan's Phenomenal Team",
            'Protocols P': 'LeAntiClutch',
            'Team Goon Cena': "Sufyan's Superb Team",
            'Dead': "Samuel's Tip-Top Team",
            'Kentucky Jr.': 'gae young',
            'gae young': 'Kentucky Jr.',
            'Last Place Projected': "Liam's Squad of Goofy Goobers",
            "Liam's Squad of Goofy Goobers": 'Last Place Projected',
            "Nathan's Phenomenal Team": 'JKimothy',
            "Sufyan's Superb Team": 'Team Goon Cena',
            "Samuel's Tip-Top Team": 'Dead'
        },
        13: {
        'LeAntiClutch': "Nathan's Phenomenal Team",
        'JKimothy': 'Dead',
        'Protocols P': "Liam's Squad of Goofy Goobers",
        'Team Goon Cena': 'Last Place Projected',
        'Dead': 'JKimothy',
        'Kentucky Jr.': "Samuel's Tip-Top Team",
        'gae young': "Sufyan's Superb Team",
        'Last Place Projected': 'Team Goon Cena',
        "Liam's Squad of Goofy Goobers": 'Protocols P',
        "Nathan's Phenomenal Team": 'LeAntiClutch',
        "Sufyan's Superb Team": 'gae young',
        "Samuel's Tip-Top Team": 'Kentucky Jr.'
        },
        
    }

        teamKey = getTeamMap()
        
    

        
        
        for team in getTeamMap():
            Matchup[13][teamKey[team]] = teamKey[lg.to_team(team).matchup(13)]

        
        Streak = {

        }
        
        for x in Matchup[1]:
            Streak[x] = {'W':0, 'L':0, 'T':0}

        NameHistory = {'410.l.136341.t.1': ['LeAntiClutch', 'LeInjured', 'LeStrain', 'LeEjected', 'LeCovid'], 
        '410.l.136341.t.10': ['JKimothy'], 
        '410.l.136341.t.2': ['Protocols P', 'Bandemic P'], 
        '410.l.136341.t.3': ['Team Goon Cena'], 
        '410.l.136341.t.4': ['Dead', 'Badedayo', 'More Dead'], 
        '410.l.136341.t.7': ['Kentucky Jr.'], 
        '410.l.136341.t.5': ['gae young'], 
        '410.l.136341.t.12': ['Last Place Projected'], 
        '410.l.136341.t.6': ["Liam's Squad of Goofy Goobers"], 
        '410.l.136341.t.9': ["Nathan's Phenomenal Team"], 
        '410.l.136341.t.8': ["Sufyan's Superb Team"], 
        '410.l.136341.t.11': ["Samuel's Tip-Top Team"]}

        TeamMapInverse = {
            'LeAntiClutch': '410.l.136341.t.1', 
            'JKimothy': '410.l.136341.t.10', 
            'Protocols P': '410.l.136341.t.2', 
            'Team Goon Cena': '410.l.136341.t.3', 
            'Dead': '410.l.136341.t.4', 
            'Kentucky Jr.': '410.l.136341.t.7', 
            'gae young': '410.l.136341.t.5', 
            'Last Place Projected': '410.l.136341.t.12', 
            "Liam's Squad of Goofy Goobers": '410.l.136341.t.6', 
            "Nathan's Phenomenal Team": '410.l.136341.t.9', 
            "Sufyan's Superb Team": '410.l.136341.t.8', 
            "Samuel's Tip-Top Team": '410.l.136341.t.11'}

    
        
        for x in range(1, lg.current_week()):

            Prediction = MatchupHistory.query.filter_by(matchup_week=x).first()
            
            for team in Prediction.winning_matchup:
                
                found = False
                for teamOpt in NameHistory[TeamMapInverse[Matchup[x][editTeamName(team)]]]:
                    
                    
                    try:
                        
                        for winningMatchup in Prediction.winning_matchup[team]:
                            if teamOpt in winningMatchup:
                                team = editTeamName(team)
                                Streak[team]['W'] += 1
                                Streak[team]['L'] = 0
                                found = True
                                break
                    except:
                        break
                if (not found):
                    team = editTeamName(team)
                    Streak[team]['L'] += 1
                    Streak[team]['W'] = 0



    
    Streak = {
        "Dead": {
            "L": 0,
            "T": 0,
            "W": 3
        },
        "JKimothy": {
            "L": 1,
            "T": 0,
            "W": 0
        },
        "Kentucky Jr.": {
            "L": 0,
            "T": 0,
            "W": 1
        },
        "Last Place Projected": {
            "L": 1,
            "T": 0,
            "W": 0
        },
        "LeAntiClutch": {
            "L": 0,
            "T": 0,
            "W": 1
        },
        "Liam's Squad of Goofy Goobers": {
            "L": 0,
            "T": 0,
            "W": 1
        },
        "Nathan's Phenomenal Team": {
            "L": 7,
            "T": 0,
            "W": 0
        },
        "Protocols P": {
            "L": 1,
            "T": 0,
            "W": 0
        },
        "Samuel's Tip-Top Team": {
            "L": 8,
            "T": 0,
            "W": 0
        },
        "Sufyan's Superb Team": {
            "L": 0,
            "T": 0,
            "W": 1
        },
        "Team Goon Cena": {
            "L": 0,
            "T": 0,
            "W": 6
        },
        "gae young": {
            "L": 1,
            "T": 0,
            "W": 0
        }
    }

    

    
   
    return Streak




    