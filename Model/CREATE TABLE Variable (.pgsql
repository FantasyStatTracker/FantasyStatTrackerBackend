CREATE TABLE Variable (
    variable_name varchar (40) PRIMARY KEY,
    variable_data varchar (400),
    updated_at TIMESTAMP
);

CREATE TABLE Prediction_History (
    prediction_week INTEGER,
    prediction_data varchar (400),
    prediction_correct INTEGER
);

CREATE TABLE Matchup_History (
    matchup_week INTEGER PRIMARY KEY,
    all_data varchar(900),
    winning_matchup varchar(900),
    leader varchar(900)
);

