from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Variable(db.Model):
    __table_args__ = {'extend_existing': True}
    variable_name = db.Column(db.String(40), primary_key=True)
    variable_data = db.Column(db.String(400))
    updated_at = db.Column(db.TIMESTAMP)


class PredictionHistory(db.Model):
    __table_args__ = {'extend_existing': True}
    prediction_week = db.Column(db.Integer, primary_key=True)
    prediction_data = db.Column(db.String(400))
    prediction_correct = db.Column(db.Integer)