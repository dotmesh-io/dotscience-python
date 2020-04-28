FROM python:3.8-slim-buster

WORKDIR /app
COPY flask-requirements.txt .
RUN pip install -r flask-requirements.txt
COPY main.py user_predict.py .

ENV FLASK_PORT "8501"

# TODO switch away from Flask webserver to something better:
CMD [ "python", "main.py" ]
