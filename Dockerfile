FROM python:3.7-slim-buster
RUN apt update -y

# libleveldb1v5 libleveldb-dev 
RUN apt-get install -y build-essential libssl-dev libffi-dev python3-dev --no-install-recommends
RUN apt-get install -y python3-leveldb --no-install-recommends

RUN pip install -U pip


COPY requirements.txt /tmp/dependencies/
RUN pip install -Ur /tmp/dependencies/requirements.txt

COPY moneybot/ /app/moneybot/
COPY app.py /app/
WORKDIR /app

ENTRYPOINT ["python"]
CMD ["app.py"]
