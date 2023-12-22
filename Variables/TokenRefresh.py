from yahoo_oauth import OAuth2
import yahoo_fantasy_api as yfa
import os
from pymongo import MongoClient

global oauth
global gm
global lg
global api_key
global db


oauth = OAuth2(None, None, from_file="oauth2.json")
gm = yfa.Game(oauth, "nba")

lg = gm.to_league(os.getenv("LEAGUE_ID"))  # 2022-23
api_key = os.getenv("API_KEY")
connection_string = "mongodb+srv://fantasy_user:mShmjJcog7iPBoVa@cluster29877.rvsjvxp.mongodb.net/?appName=mongosh+2.0.0".format(
    credentials=os.getenv("MONGO_PASS"), username=os.getenv("MONGO_USER")
)
print(connection_string)
client = MongoClient(connection_string)
db = client.sample_training

if not oauth.token_is_valid():
    oauth.refresh_access_token()
