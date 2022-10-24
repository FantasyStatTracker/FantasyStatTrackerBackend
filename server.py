import os
from flask import Flask
from flask_cors import CORS


from Model.variable import db
from routes.RelevantData import RelevantData
from routes.Prediction import Prediction
from routes.FullData import FullData
from routes.WinningMatchup import WinningMatchup
from routes.Admin import Admin
from routes.NewApi import Api
from routes.PlayerStatistics import PlayerStatistics

app = Flask(__name__)


app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("KEY")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
cors = CORS(app)

db.init_app(app)

# app.register_blueprint(test_blueprint)
app.register_blueprint(RelevantData)
app.register_blueprint(Prediction)
app.register_blueprint(FullData)
app.register_blueprint(WinningMatchup)
app.register_blueprint(Admin)
app.register_blueprint(Api)
app.register_blueprint(PlayerStatistics)


if __name__ == "__main__":
    dev = False
    portVar = ""
    if dev:
        portVar = 8000
        with app.app_context():
            pass
    else:
        portVar = os.environ.get("PORT", 80)
    app.run(host="localhost", port=portVar, debug=dev)
