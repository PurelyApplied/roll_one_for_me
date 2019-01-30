FROM ubuntu

LABEL maintainer="Patrick Rhomberg <coding@patrhom.com>"

# Throughout, we use a blank env SUDO for easy local, non-dockerized testing.

# Get gcloud ready
RUN export CLOUD_SDK_REPO="cloud-sdk-$(lsb_release -c -s)" \
 && echo "deb http://packages.cloud.google.com/apt $CLOUD_SDK_REPO main" | ${SUDO} tee -a /etc/apt/sources.list.d/google-cloud-sdk.list \
 && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | ${SUDO} apt-key add - \
 && ${SUDO} apt-get update \
 && ${SUDO} apt-get install -y google-cloud-sdk \
 && gcloud init

# Get Docker ready
RUN ${SUDO} apt update \
 && ${SUDO} apt install -y \
      apt-transport-https \
      ca-certificates \
      curl \
      gnupg-agent \
      software-properties-common \
 && curl -fsSL https://download.docker.com/linux/ubuntu/gpg | ${SUDO} apt-key add - \
 && ${SUDO} apt-key fingerprint 0EBFCD88 \
 && ${SUDO} add-apt-repository \
     "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
     $(lsb_release -cs) \
     stable" \
 && ${SUDO} apt update \
 && ${SUDO} apt install -y docker-ce \
 && ${SUDO} groupadd docker || true \
 && ${SUDO} usermod -aG docker purelyapplied \

# gcloud should play nicely
RUN gcloud auth configure-docker

# Get rofm ready
RUN ${SUDO} apt update \
 && ${SUDO} apt install -y python3 python3-pip git \
 && pip3 install --upgrade pip \
 && git clone https://github.com/PurelyApplied/roll_one_for_me.git \
 && pip3 install -r roll_one_for_me/requirements.txt \
 && mkdir roll_one_for_me/logs/
