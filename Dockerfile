FROM python:3.8-slim

RUN apt-get update && apt-get install -y cron

RUN crontab -l | { cat; echo "*/10 * * * * python /app/synchronize_cat_tags.py"; } | crontab -

ADD ./synchronize_cat_tags.py ./synchronize_entrypoint.sh ./requirements.txt /app
WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt


ENTRYPOINT "/bin/sh -c '/app/synchronize_entrypoint.sh'"
CMD ["cron", "-f"]
