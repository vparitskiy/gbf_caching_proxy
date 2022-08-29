FROM python:3.10.5-slim-bullseye

ARG DEBIAN_FRONTEND=noninteractive
ARG APT_KEY_DONT_WARN_ON_DANGEROUS_USAGE=1

ENV \
  PYTHONUNBUFFERED=1 \
  PYTHONDONTWRITEBYTECODE=1 \
  PIP_DISABLE_PIP_VERSION_CHECK=on

RUN apt-get -q update && apt-get -qy install \
    locales \
    # apt-get cleanup
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN sed -i -e "s/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/" /etc/locale.gen \
    && dpkg-reconfigure locales \
    && update-locale LANG=en_US.UTF-8

ENV LANG=en_US.UTF-8 LANGUAGE=en_US:en LC_ALL=en_US.UTF-8

WORKDIR /srv/server

# user setup
ARG UNAME=appuser
ARG UID=0
ARG GID=$UID
RUN groupadd -g $GID -o $UNAME
RUN useradd -m -u $UID -g $GID -o -s /bin/bash $UNAME

ENV PATH="/home/${UNAME}/.local/bin:${PATH}"

USER ${UNAME}

COPY ./requirements.txt /tmp/requirements.txt
RUN pip install --no-input --no-cache-dir -r /tmp/requirements.txt

COPY --chown=${UID}:${GID} ./gbf_caching_proxy /srv/server