import os
from flask import Flask
from flask_cors import CORS

# # # # # # # # # from Model.variable import db
from routes.RelevantData import RelevantData
from routes.Prediction import Prediction
from routes.FullData import FullData
from routes.WinningMatchup import WinningMatchup
from routes.Admin import Admin
from routes.NewApi import Api
#from routes.PlayerStatistics import PlayerStatistics
from routes.TeamInformtion import TeamInformation
from cache import cache
from Variables.TokenRefresh import lg, oauth, gm
from yahoo_oauth import OAuth2
import yahoo_fantasy_api as yfa
from dotenv import load_dotenv

load_dotenv()

config = {"DEBUG": True, "CACHE_TYPE": "SimpleCache", "CACHE_DEFAULT_TIMEOUT": 300}
app = Flask(__name__)

app.config.from_mapping(config)

# app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("KEY")
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
cors = CORS(app)

cache.init_app(app)
# db.init_app(app)

# app.register_blueprint(test_blueprint)
app.register_blueprint(RelevantData)
app.register_blueprint(Prediction)
app.register_blueprint(FullData)
app.register_blueprint(WinningMatchup)
app.register_blueprint(Admin)
app.register_blueprint(Api)
# app.register_blueprint(PlayerStatistics)
app.register_blueprint(TeamInformation)


if __name__ == "__main__":
    port = ""
    environment = True
    if environment:
        port = 8000
        with app.app_context():
            pass
    else:
        port = os.getenv("PORT", 80)
    app.run(host="0.0.0.0", port=port, debug=environment)
