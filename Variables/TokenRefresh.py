from yahoo_oauth import OAuth2
import yahoo_fantasy_api as yfa
import json

global oauth 
global gm
global lg
global apiKey


oauth = OAuth2(None, None, from_file='oauth2.json')
gm = yfa.Game(oauth, 'nba')
#lg = gm.to_league('402.l.67232') #2020-21
lg = gm.to_league('410.l.136341') #2021-22

f = open('./apiKey.json')
apiKey = json.load(f)["access_key"]
f.close()

if not oauth.token_is_valid():
    oauth.refresh_access_token()

