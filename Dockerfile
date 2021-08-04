FROM python:3.8-slim

ADD ./requirements.txt ./synchronize_entrypoint.sh /app/
WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt && chmod +x /app/synchronize_entrypoint.sh

ADD ./helpers.py ./defs.py ./synchronize_cat_tags.py /app/

ENTRYPOINT [ "/app/synchronize_entrypoint.sh" ] 
CMD [ "60", "synchronize_cat_tags.py" ]
