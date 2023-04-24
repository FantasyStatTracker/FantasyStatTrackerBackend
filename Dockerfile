FROM python:3.8.3-slim

ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV YEAR="2023"
ENV ENVIRONMENT="true"
ENV API_KEY="<648)k?UdULc'W+z"
ENV LEAGUE_ID="418.l.25891"
ENV URL="https://www.basketball-reference.com/leagues/NBA_${YEAR}_per_game.html"
ENV KEY="postgres://qccabsoqpyllpe:479fca0e9146bad9e6bac6e90089f52a6190ea303364b47d55ea62e9ad04cc2f@ec2-52-205-61-230.compute-1.amazonaws.com:5432/ddvr9nfvico5c4"


RUN apt-get update \
    && apt-get -y install libpq-dev gcc curl

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt



RUN python3 -m pip install -r requirements.txt

COPY . /app

EXPOSE 8000

CMD ["python", "server.py"]

