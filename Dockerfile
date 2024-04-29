FROM python:3.12.3-alpine3.18
COPY requirements.txt .
COPY src/ .
RUN pip3 install -r requirements.txt
RUN python3 main.py