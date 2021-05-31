# base image
# FROM python:3.8.0-alpine
FROM python:3.6-alpine3.9

LABEL MAINTAINER="Dhiraj Patra <dpatra@presto.com>"

WORKDIR /api

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update \
    && apk add --no-cache --virtual build-dependencies \
    build-base \
    gcc \
    wget \
    python-dev \
    git \
    && pip3 install -U pip
RUN apk add libc-dev curl-dev libevent-dev python3-dev libressl-dev

RUN apk add --no-cache --virtual .build-deps libxslt-dev && \
    apk add --no-cache libxslt && \
    pip install --no-cache-dir lxml>=3.5.0 && \
    apk del .build-deps

# # for chaterbot
# ENV SPACY_VERSION 2.0.3
# RUN pip3 install -U spacy==${SPACY_VERSION} \
#     && python3 -m spacy download en \
#     && python3 -m spacy download xx

ENV C_FORCE_ROOT true

ENV HOST 0.0.0.0
ENV PORT 5000
ENV DEBUG true


# ENV GROUP_ID=1000 \
#     USER_ID=1000

# install requirements
ADD ./requirements.txt /api/requirements.txt
RUN pip install --upgrade pip
RUN pwd
# RUN pip install -r requirements.txt

RUN \
 apk add --no-cache postgresql-libs && \
 apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
 python3 -m pip install -r requirements.txt --no-cache-dir && \
 apk --purge del --no-cache .build-deps

# copy initial psql to create user and database
COPY ./init.sql /docker-entrypoint-initdb.d/

# copy entrypoint.sh
COPY ./entrypoint.sh /api/


# expose the app port
EXPOSE 5000

RUN pip install gunicorn

COPY . /api


# create user group and user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

RUN chown -R appuser:appgroup /usr/src
RUN chown -R appuser:appgroup /home
RUN chown -R appuser:appgroup /api
# RUN chmod -R 755 /usr/src/app
RUN chmod -R 777 /var/log
USER appuser
RUN whoami

ENTRYPOINT ["/api/entrypoint.sh"]