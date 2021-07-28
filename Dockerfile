FROM python:3.8-slim

ADD . /app
WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt

RUN crontab -l | {cat; echo "1/10 * * * * python /app/synchronize_cat_tags.py"; } | crontab -

CMD ['cron' '-f']

