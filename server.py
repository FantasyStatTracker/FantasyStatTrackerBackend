import os
from flask import Flask
from flask_cors import CORS

from routes.RelevantData import RelevantData
from routes.WinningMatchup import WinningMatchup
from routes.NewApi import Api
from cache import cache
from Variables.TokenRefresh import lg, oauth, gm
from yahoo_oauth import OAuth2
import yahoo_fantasy_api as yfa
from dotenv import load_dotenv

load_dotenv()

config = {"DEBUG": True, "CACHE_TYPE": "SimpleCache", "CACHE_DEFAULT_TIMEOUT": 300}
app = Flask(__name__)

app.config.from_mapping(config)

cors = CORS(app)

cache.init_app(app)


app.register_blueprint(RelevantData)
app.register_blueprint(WinningMatchup)
app.register_blueprint(Api)

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
