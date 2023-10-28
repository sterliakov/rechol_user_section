FROM python:3.11-slim as build
SHELL ["/bin/bash", "-e", "-u", "-x", "-o", "pipefail", "-c"]

ARG REQUIREMENTS_FILE=requirements.txt
ARG DEBIAN_FRONTEND=noninteractive

COPY requirements.txt /requirements.txt

RUN BUILD_DEPS="build-essential libpcre3-dev libpq-dev git pkg-config nodejs npm gettext" && \
    apt-get update && apt-get install -y --no-install-recommends $BUILD_DEPS && \
    python -m venv venv && \
    . venv/bin/activate && \
    pip install -U --no-cache-dir pip setuptools wheel && \
    pip install -U --no-cache-dir gunicorn && \
    pip install --no-cache-dir -r /${REQUIREMENTS_FILE:-requirements.dev.txt} && \
    npm i -g bower sass && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app
RUN . /venv/bin/activate && \
    DJANGO_SECRET_KEY=1 ./manage.py bower install && \
    DJANGO_SECRET_KEY=1 ./manage.py collectstatic && \
    COMPRESSOR_CACHE=filesystem DJANGO_SECRET_KEY=1 ./manage.py compress && \
    DJANGO_SECRET_KEY=1 ./manage.py compilemessages

FROM python:3.11-slim as deploy
SHELL ["/bin/bash", "-e", "-u", "-x", "-o", "pipefail", "-c"]

ARG APP_USER=rechol
ARG APP_HOME=/home/rechol
ARG DEBIAN_FRONTEND=noninteractive

RUN groupadd -r ${APP_USER} && useradd --no-log-init -r -g ${APP_USER} ${APP_USER} && \
    RUN_DEPS="libpcre3 mime-support postgresql-client" && \
    apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends $RUN_DEPS && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir -p /var/www/rechol_user_section/media/ && \
    chown -R ${APP_USER}:${APP_USER} /var/www/rechol_user_section/media/

WORKDIR ${APP_HOME}
# Patch
COPY --from=build /venv /venv
COPY --from=build --chown=${APP_USER}:${APP_USER} /app/patches/locale_ru/ /venv/lib/python3.11/site-packages/django/conf/locale/ru/LC_MESSAGES
COPY --from=build --chown=${APP_USER}:${APP_USER} /app/static_files/compressed/manifest.json static_files/compressed/manifest.json
COPY --from=build --chown=${APP_USER}:${APP_USER} /app ${APP_HOME}

USER ${APP_USER}:${APP_USER}
# We use single worker here, because gunicorn cannot handle multiple async eventlet
# workers. We need eventlet to support websockets.
ENTRYPOINT ["/bin/bash", "-c", "/venv/bin/gunicorn -w 3 --timeout 3600 rechol_user_section.wsgi:application -b 0.0.0.0:${APP_PORT} --preload"]

FROM nginx:1.25.2 as nginx
SHELL ["/bin/sh", "-e", "-u", "-x", "-c"]

ARG NGINX_CONF

RUN rm /etc/nginx/conf.d/default.conf
COPY configs/${NGINX_CONF:-site.conf} /etc/nginx/templates/site.conf.template
COPY --from=build --chmod=777 --chown=root:root /app/static_files/ /home/rechol/static/
