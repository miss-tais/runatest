FROM python:3.8

# set work directory
#WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
COPY ./web/requirements /requirements
RUN pip install -r /requirements/local.txt

# copy entrypoint.sh
COPY ./web/compose/local/docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

COPY . .

ENTRYPOINT ["/docker-entrypoint.sh"]
