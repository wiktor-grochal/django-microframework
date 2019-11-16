FROM python:3.7-alpine3.8

RUN mkdir /sender
RUN mkdir /microframework
COPY ./examples/sender/requirements.txt /sender
WORKDIR /sender

RUN apk update && \
 apk add postgresql-libs && \
 apk add --virtual .build-deps git gcc musl-dev postgresql-dev linux-headers && \
 python3 -m pip install -r requirements.txt --no-cache-dir && \
 apk --purge del .build-deps

COPY ./examples/sender/ /sender/
COPY ./ /microframework/
RUN python /microframework/setup.py install
WORKDIR /sender/src
CMD ["python3", "manage.py", "runserver_plus", "[::]:8000"]
