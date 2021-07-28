FROM python:3.8-slim

RUN apt-get update && apt-get install -y cron

RUN crontab -l | { cat; echo "*/1 * * * * python /app/synchronize_cat_tags.py"; } | crontab -

ADD ./helpers.py ./defs.py ./synchronize_cat_tags.py ./synchronize_entrypoint.sh ./requirements.txt /app/
WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt && chmod +x /app/synchronize_entrypoint.sh


ENTRYPOINT [ "/app/synchronize_entrypoint.sh" ] 
CMD ["60"]
