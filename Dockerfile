# pull the official docker image
FROM python:3.11.5
WORKDIR ./Users/zhuchka/Desktop/ZhuchkaKeyboards
COPY ./app ./app
COPY ./requirements.txt
RUN pip3 install -r requirements.txt