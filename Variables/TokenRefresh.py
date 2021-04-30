from yahoo_oauth import OAuth2
import yahoo_fantasy_api as yfa

oauth = OAuth2(None, None, from_file='oauth2.json')

if not oauth.token_is_valid():
    oauth.refresh_access_token()


def token():
    gm = yfa.Game(oauth, 'nba')
    lg = gm.to_league('402.l.67232') 
    data = {
        "gm": yfa.Game(oauth, 'nba'),
        "lg": gm.to_league('402.l.67232'),
        "oauth":oauth 
    }
    return data