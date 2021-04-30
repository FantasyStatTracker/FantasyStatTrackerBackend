from yahoo_oauth import OAuth2
import yahoo_fantasy_api as yfa
import json

global oauth 
global gm
global lg
creds = {
    "consumer_key": "dj0yJmk9RDl6d0tLZnhTbDZlJmQ9WVdrOWEzWlhORlZ6TkRJbWNHbzlNQT09JnM9Y29uc3VtZXJzZWNyZXQmc3Y9MCZ4PTM0",
    "consumer_secret": "673ee9188f6641cc5c22423d885ff6370b791d66"
}
with open('oauth2.json', "w") as f:
   f.write(json.dumps(creds))

oauth = OAuth2(None, None, from_file='oauth2.json')
gm = yfa.Game(oauth, 'nba')
lg = gm.to_league('402.l.67232') 

if not oauth.token_is_valid():
    oauth.refresh_access_token()