FROM python:3.8-slim

ADD ./requirements.txt /app/
WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt

# ADD ./helpers.py ./defs.py ./synchronize_cat_tags.py /app/
COPY ./*.py /app/

COPY rootfs /

RUN chmod +x /usr/bin/entrypoint.sh
ENTRYPOINT [ "/usr/bin/entrypoint.sh" ] 
CMD [ "60", "synchronize_cat_tags.py" ]
