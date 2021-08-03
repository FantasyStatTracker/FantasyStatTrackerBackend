@app.route("/schedule", methods=['GET']) #schedule (not needed anymore really)
def getSchedule():
    r = requests.get(
        'https://data.nba.com/data/10s/v2015/json/mobile_teams/nba/2020/league/00_full_schedule.json')

    Game = {}
    data = r.json()

    for x in data['lscd']:
        Game[x["mscd"]["mon"]] = {}

        for y in x["mscd"]["g"]:
            Game[x["mscd"]["mon"]][y["gdte"]] = []
        for y in x["mscd"]["g"]:
            Game[x["mscd"]["mon"]][y["gdte"]].append(
                (y["v"]["ta"], y["h"]["ta"]))

    return Game