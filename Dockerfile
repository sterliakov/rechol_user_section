FROM python:3.10-slim
SHELL ["/bin/bash", "-e", "-u", "-x", "-o", "pipefail", "-c"]

ARG APP_USER
ARG APP_PORT
ARG REQUIREMENTS_FILE=requirements.txt
ARG APP_HOME=/home/rechol
ARG DEBIAN_FRONTEND=noninteractive

RUN groupadd -r ${APP_USER} && useradd --no-log-init -r -g ${APP_USER} ${APP_USER}

RUN RUN_DEPS=" \
    libpcre3 \
    mime-support \
    postgresql-client \
    " && \
    apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends $RUN_DEPS && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /requirements.txt

RUN BUILD_DEPS="build-essential libpcre3-dev libpq-dev git pkg-config" && \
    apt-get update && apt-get install -y --no-install-recommends $BUILD_DEPS && \
    pip install -U --no-cache-dir pip setuptools wheel && \
    pip install -U --no-cache-dir gunicorn && \
    pip install --no-cache-dir -r /${REQUIREMENTS_FILE:-requirements.dev.txt} && \
    apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false $BUILD_DEPS && \
    rm -rf /var/lib/apt/lists/*

# Patch
COPY --chown=${APP_USER}:${APP_USER} ./patches/locale_ru/ /usr/local/lib/python3.10/site-packages/django/conf/locale/ru/LC_MESSAGES

COPY --chown=${APP_USER}:${APP_USER} . ${APP_HOME}
RUN mkdir -p /var/www/rechol_user_section/media/ &&\
    chown -R ${APP_USER}:${APP_USER} /var/www/rechol_user_section/media/
WORKDIR ${APP_HOME}

USER ${APP_USER}:${APP_USER}
# We use single worker here, because gunicorn cannot handle multiple async eventlet
# workers. We need eventlet to support websockets.
ENTRYPOINT ["/bin/bash", "-c", "gunicorn -w 3 --timeout 3600 rechol_user_section.wsgi:application -b 0.0.0.0:${APP_PORT} --preload"]
