from yahoo_oauth import OAuth2
import yahoo_fantasy_api as yfa
import os

global oauth
global gm
global lg
global api_key


oauth = OAuth2(None, None, from_file="oauth2.json")
gm = yfa.Game(oauth, "nba")
lg = gm.to_league(os.getenv("LEAGUE_ID"))  # 2022-23
api_key = os.getenv("API_KEY")

if not oauth.token_is_valid():
    oauth.refresh_access_token()
