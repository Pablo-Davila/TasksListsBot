FROM python:3.8.10

WORKDIR /code

RUN mkdir /data
VOLUME [ "/data" ]

ADD ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ADD ./tasks_lists_bot.py .

CMD [ "python3", "tasks_lists_bot.py" ]
