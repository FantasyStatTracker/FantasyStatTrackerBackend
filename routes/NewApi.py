
from flask import Blueprint, request, jsonify
from flask.signals import request_tearing_down
from flask_cors import  cross_origin
import json
import requests
from Variables.TokenRefresh import lg, apiKey
from .FullData import test
from .WinningMatchup import winning, getWins
from .RelevantData import lastWeekRoster
from  HelperMethods.helper import getMatchups
from .Prediction import predict
from basketball_reference_scraper.players import get_stats, get_game_logs, get_player_headshot



Api_Blueprint = Blueprint('Api', __name__)

from Model.variable import MatchupHistory, db


@Api_Blueprint.route('/v1/check', methods=['GET']) #winning 
@cross_origin()
def updateRosterStats():

    print(get_stats("Ben Simmons", 'PER_GAME')[-1:].to_string())
    return ""