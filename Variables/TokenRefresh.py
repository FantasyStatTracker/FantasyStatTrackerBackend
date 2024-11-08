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

stat_map = {
    "5": "FG%",
    "8": "FT%",
    "10": "3PTM",
    "12": "PTS",
    "15": "REB",
    "16": "AST",
    "17": "ST",
    "18": "BLK",
    "19": "TO",
}

stat_array = ["FG", "FT", "ThreePTM", "PTS", "REB", "AST", "ST", "BLK", "TO"]

class LeagueData:
    def __init__(self):
        pass

class TeamStats:
    def __init__(self, **kwargs):
        self.FG = kwargs.get("FG%", 0.0)
        self.FT = kwargs.get("FT%", 0.0)
        self.ThreePTM = kwargs.get("3PTM", 0)
        self.PTS = kwargs.get("PTS", 0)
        self.REB = kwargs.get("REB", 0)
        self.AST = kwargs.get("AST", 0)
        self.ST = kwargs.get("ST", 0)
        self.BLK = kwargs.get("BLK", 0)
        self.TO = kwargs.get("TO", 0)

    def get_category_array(self):
        return ["FG%", "FT%", "3PTM", "PTS", "REB", "AST", "ST", "BLK", "TO"]

class WinningMatchup:
    def __init__(self, team_name: str, category_won: list):
        self.team_name = team_name
        self.category_won = category_won
    
    def jsonify_matchup(self):
        res = {}
        res["team_name"] = self.team_name
        res["category_won"] = self.category_won

        return res

class Team:
    def __init__(self, team_stats: TeamStats, team_id: str, team_name: str, team_photo_url: str):
        self.team_stats = team_stats
        self.team_id = team_id
        self.team_name = team_name
        self.team_photo_url = team_photo_url

    def get_name(self) -> str:
        return self.team_name
    
    def set_winning_matchups(self, winning_matchup):
        self.winning_matchup = winning_matchup
        self.winning_matchup_count = len(winning_matchup)

    def jsonify_winning_matchups(self):
        res = []
        for winning_matchup in self.winning_matchup:
            res.append(winning_matchup.jsonify_matchup())
        return res

def build_stat_obj(stat_array: list, stat_map: dict) -> dict:
    stats = {}
    for stat in stat_array:
        stat_id = stat["stat"]["stat_id"]

        if stat_id in stat_map:
            category_key = stat_map[stat_id]
            stat_value = float(stat["stat"]["value"]) if stat["stat"]["value"] else 0.0
            stats[category_key] = stat_value

    return stats

def compare_stats(team_stats: TeamStats, team_stats_compare: TeamStats, team_name: str) -> WinningMatchup:
    team_stats_dict = team_stats.__dict__
    team_stats_compare_dict = team_stats_compare.__dict__

    winning = [k for k in team_stats_dict if float(team_stats_dict[k]) > float(team_stats_compare_dict[k]) and k != "TO"]
    if team_stats_dict["TO"] < team_stats_compare_dict["TO"]:
        winning.append("TO")
    if len(winning) > 4:
        return WinningMatchup(team_name, winning)
    return None

def test2(lg, week=None):

    full_matchup_information = lg.matchups(week)

    matchups = full_matchup_information["fantasy_content"]["league"][1]["scoreboard"]["0"]["matchups"]

    res = {}
    for x in range(0, int(matchups["count"])):
        team1 = matchups[str(x)]["matchup"]["0"]["teams"]["0"]["team"]
        team2 = matchups[str(x)]["matchup"]["0"]["teams"]["1"]["team"]
        team1stats = team1[1]["team_stats"]["stats"]
        team2stats = team2[1]["team_stats"]["stats"]

        team1stats = TeamStats(**build_stat_obj(team1stats, stat_map))
        team2stats = TeamStats(**build_stat_obj(team2stats, stat_map))

        team1Obj = Team(team1stats, team1[0][0]["team_key"], team1[0][2]["name"], team1[0][5]["team_logos"][0]["team_logo"]["url"])
        team2Obj = Team(team2stats, team2[0][0]["team_key"], team2[0][2]["name"], team2[0][5]["team_logos"][0]["team_logo"]["url"])

        res[team1[0][0]["team_key"]] = team1Obj
        res[team2[0][0]["team_key"]] = team2Obj



    for team in res:
        winning_matchups = []
        for team_compare in res:
            if team == team_compare:
                continue

            matchup_won = compare_stats(res[team].team_stats, res[team_compare].team_stats, res[team_compare].team_name)
            if matchup_won is not None:
                winning_matchups.append(matchup_won)
        
        res[team].set_winning_matchups(winning_matchups)

    return res


if not oauth.token_is_valid():
    oauth.refresh_access_token()
