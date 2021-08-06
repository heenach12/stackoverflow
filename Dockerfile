# FROM ubuntu:20.04
FROM python:3.9.1

RUN apt-get update
RUN apt-get install python3 -y
RUN apt-get install python3-pip -y
RUN apt-get install vim -y

WORKDIR /opt/apps/flaskapi

COPY stackoverflow/requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 5000

ENV PYTHONPATH "${PYTHONPATH}:/usr/lib/python3.8"

# ENTRYPOINT ["python3"]
# CMD ["stackoverflow/app.py",  "--host=0.0.0.0"]

RUN chmod u+x ./stackoverflow/entrypoint.sh
ENTRYPOINT ["./stackoverflow/entrypoint.sh"]