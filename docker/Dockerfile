FROM python:3.7-alpine as base
LABEL maintainer="robitmoh"
LABEL description="Infpyng can ping multiple hosts at once and write data to InfluxDB"

FROM base as builder

RUN mkdir /install
WORKDIR /install

COPY requirements.txt /requirements.txt

RUN pip install --prefix /install --no-cache-dir -r /requirements.txt

FROM base

COPY --from=builder /install /usr/local
COPY include/ /infpyng/include/
COPY infpyng.py /infpyng/
COPY docker/config/ /infpyng/docker/config/
copy docker/docker_start.sh /infpyng/docker_start.sh
RUN  chmod 755 /infpyng/docker_start.sh
WORKDIR /infpyng

RUN apk add --no-cache fping tzdata gettext
CMD ./docker_start.sh
