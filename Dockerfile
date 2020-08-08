FROM python:3.6.9-slim-buster

WORKDIR /app
COPY requirements.txt /app/

COPY . /app

RUN apt-get update \
&& apt-get install gcc -y \
&& apt-get clean \
&& pip install -r requirements.txt

CMD python ./is-alive/build_config.py && gunicorn -t 3600 --log-level=debug is-alive:app