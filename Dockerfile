FROM ubuntu

LABEL maintainer="Patrick Rhomberg <coding@patrhom.com>"

COPY praw.ini .config/praw.ini

RUN apt-get update -q \
 && apt-get install -y python3 python3-pip git \
 && git clone --branch develop https://github.com/PurelyApplied/roll_one_for_me.git \
 && pip3 install -r roll_one_for_me/requirements.txt

WORKDIR roll_one_for_me
ENTRYPOINT /usr/bin/python3 run_legacy.py --long-lived

HEALTHCHECK --start-period=60s --interval=15m CMD pgrep -af run_legacy.py
