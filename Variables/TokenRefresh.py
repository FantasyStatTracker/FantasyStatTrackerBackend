from yahoo_oauth import OAuth2
import yahoo_fantasy_api as yfa
import json

global oauth 
global gm
global lg
global tm

oauth = OAuth2(None, None, from_file='oauth2.json')
gm = yfa.Game(oauth, 'nba')
lg = gm.to_league('402.l.67232') 

if not oauth.token_is_valid():
    oauth.refresh_access_token()