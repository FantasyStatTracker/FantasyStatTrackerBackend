from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Variable(db.Model):
    __table_args__ = {'extend_existing': True}
    variable_name = db.Column(db.String(40), primary_key=True)
    variable_data = db.Column(db.String(400))
    updated_at = db.Column(db.TIMESTAMP)