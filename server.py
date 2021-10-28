import os
from flask import Flask, request, Blueprint, render_template
from flask_cors import CORS, cross_origin
from Model.variable import db, Variable
from dbkey import key
#from routes.Test import *
from routes.RelevantData import *
from routes.Prediction import *
from routes.FullData import *
from routes.WinningMatchup import *
#from routes.Test import *
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = key
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
cors = CORS(app)

db.init_app(app)

#app.register_blueprint(test_blueprint)
app.register_blueprint(RelevantData)
app.register_blueprint(Prediction_Blueprint)
app.register_blueprint(FullData)
app.register_blueprint(WinningMatchup_Blueprint)




if __name__ == '__main__':
    dev = True
    portVar = ""
    if (dev):
        portVar = 8000
        with app.app_context():
            pass
    else:
        portVar = os.environ.get('PORT', 80)
    app.run(host="localhost", port=portVar, debug=dev)
