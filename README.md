### `python server.py`


1. source .venv/bin/activate
2. pip -r install requirements.txt
3. gunicorn --bind 0.0.0.0:8000 wsgi:app

todo: Create jenkins script or Travis to automate this
