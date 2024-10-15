FROM python:3.12

RUN python3 -m venv /opt/venv

COPY requirements.txt .

COPY .env .

RUN . /opt/venv/bin/activate && pip install -r requirements.txt

COPY main.py .

EXPOSE 443 80

CMD . /opt/venv/bin/activate && exec python3 main.py
