FROM python:3.7-slim-buster
RUN apt update -y

RUN apt-get install -y build-essential libssl-dev libffi-dev python3-dev --no-install-recommends
RUN apt-get install -y libleveldb1d libleveldb-dev python3-leveldb --no-install-recommends

RUN pip install -U pip


COPY requirements.txt /tmp/dependencies/
RUN pip install -Ur /tmp/dependencies/requirements.txt

COPY moneybot/ /app/moneybot/
COPY config.yml logging.yml app.py /app/
WORKDIR /app

ENTRYPOINT ["python"]
CMD ["app.py"]
