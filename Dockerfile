FROM python:3.11

COPY osn/ /app/osn
COPY api.py /app
COPY requirements.txt /app

WORKDIR /app

RUN pip install -r requirements.txt
RUN pip install gunicorn

EXPOSE 8000

CMD gunicorn -w 1 -b 0.0.0.0 -t 600 api:app
