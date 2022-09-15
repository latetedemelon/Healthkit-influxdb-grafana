# Following along with
# https://www.ivaylopavlov.com/charting-apple-healthkit-data-in-grafana/#.YyNSgi-B3yI
# https://www.freecodecamp.org/news/how-to-dockerize-a-flask-app/

FROM python:3.9-buster

WORKDIR /python-docker

COPY . .

RUN pip3 install -r requirements.txt

EXPOSE 5353/tcp
EXPOSE 80/tcp

CMD [ "python3.9", "app.py"]