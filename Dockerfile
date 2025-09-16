FROM python:3.13-slim

WORKDIR /code

RUN apt-get update && apt-get upgrade -y && apt-get clean && rm -rf /var/lib/apt/lists/*
RUN mkdir /data
VOLUME [ "/data" ]

ADD ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ADD ./tasks_lists_bot.py .

CMD [ "python3", "tasks_lists_bot.py" ]
