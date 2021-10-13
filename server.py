import os
from flask import Flask, request, Blueprint, render_template
from flask_cors import CORS, cross_origin

from routes.Test import *
from routes.RelevantData import *
from routes.Prediction import *
from routes.FullData import *
from routes.WinningMatchup import *

app = Flask(__name__)

cors = CORS(app)

app.register_blueprint(test_blueprint)
app.register_blueprint(RelevantData)
app.register_blueprint(Prediction_Blueprint)
app.register_blueprint(FullData)
app.register_blueprint(WinningMatchup_Blueprint)


if __name__ == '__main__':
    dev = False
    portVar = ""
    if (dev):
        portVar = 8000
    else:
        portVar = os.environ.get('PORT', 80)
    app.run(host="localhost", port=portVar, debug=dev)
