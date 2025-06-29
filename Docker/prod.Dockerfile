FROM python:3.11-slim

COPY ./src/requirements.txt ./src/usr/app/requirements.txt
RUN pip install -r /src/usr/app/requirements.txt
WORKDIR /src/usr/app
COPY ./src/ /src/usr/app/

CMD ["python","-u","kafka_consumer.py"]