FROM alpine:latest

LABEL maintainer="Patrick Rhomberg <coding@patrhom.com>"

RUN apk update \
 && apk add python3 git \
 && pip3 install --upgrade pip \
 && git clone https://github.com/PurelyApplied/roll_one_for_me.git \
 && pip3 install -r roll_one_for_me/requirements.txt \
 && mkdir roll_one_for_me/logs/

COPY praw.ini roll_one_for_me/praw.ini

WORKDIR roll_one_for_me
ENTRYPOINT /usr/bin/python3 run_legacy.py --long-lived

HEALTHCHECK --start-period=60s --interval=15m CMD pgrep -af run_legacy.py
