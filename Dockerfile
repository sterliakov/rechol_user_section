FROM public.ecr.aws/docker/library/node:20.18-alpine AS npm

WORKDIR /app
RUN npm i bootstrap@4.6.2

FROM python:3.11-slim AS get-sass
WORKDIR /sass
ADD https://github.com/sass/dart-sass/releases/download/1.80.3/dart-sass-1.80.3-linux-x64.tar.gz /sass/archive.tar.gz
RUN tar xzf ./archive.tar.gz

FROM python:3.11-slim AS build
SHELL ["/bin/bash", "-e", "-u", "-x", "-o", "pipefail", "-c"]

ARG REQUIREMENTS_FILE=requirements.txt
ENV DEBIAN_FRONTEND=noninteractive
ENV COMPRESSOR_CACHE=filesystem
ENV DJANGO_SECRET_KEY=1
ENV USER_MODEL="auth.User"

COPY requirements.txt /requirements.txt

# hadolint ignore=DL3008,SC1091
RUN BUILD_DEPS="build-essential libpcre3-dev libpq-dev git pkg-config gettext" && \
    apt-get update && apt-get install -y --no-install-recommends $BUILD_DEPS && \
    python -m venv venv && \
    . venv/bin/activate && \
    pip install -U --no-cache-dir 'pip>=23.3.1' 'setuptools>=68.2.2' 'wheel>=0.41.3' && \
    pip install -U --no-cache-dir 'gunicorn~=21.2.0' && \
    pip install --no-cache-dir -r /${REQUIREMENTS_FILE:-requirements.dev.txt} && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY manage.py ./
COPY rechol_user_section/ ./rechol_user_section/
COPY users/__init__.py ./users/__init__.py

COPY patches/ ./patches/
COPY users/locale ./users/locale
# hadolint ignore=SC1091
RUN . /venv/bin/activate && ./manage.py compilemessages

COPY users/static ./users/static
COPY --from=npm /app/node_modules node_modules
COPY --from=get-sass /sass/dart-sass/ /tmp/sass/
# hadolint ignore=SC1091
RUN . /venv/bin/activate && ./manage.py collectstatic

COPY users/templates ./users/templates
COPY users/templatetags ./users/templatetags
# hadolint ignore=SC1091
RUN . /venv/bin/activate && SASS_EXECUTABLE=/tmp/sass/sass ./manage.py compress && rm -rf node_modules


FROM python:3.11-slim AS deploy
SHELL ["/bin/bash", "-e", "-u", "-x", "-o", "pipefail", "-c"]

ARG APP_USER=rechol
ARG APP_HOME=/home/rechol
ENV DEBIAN_FRONTEND=noninteractive

# hadolint ignore=DL3008
RUN groupadd -r ${APP_USER} && useradd --no-log-init -r -g ${APP_USER} ${APP_USER} && \
    apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends libpcre3 mime-support postgresql-client && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir -p /var/www/rechol_user_section/media/ && \
    chown -R "${APP_USER}:${APP_USER}" /var/www/rechol_user_section/media/

WORKDIR ${APP_HOME}
# Patch
COPY --from=build /venv /venv
COPY --from=build --chown=${APP_USER}:${APP_USER} /app/patches/locale_ru/ /venv/lib/python3.11/site-packages/django/conf/locale/ru/LC_MESSAGES
COPY --from=build --chown=${APP_USER}:${APP_USER} /app/static_files/compressed/manifest.json static_files/compressed/manifest.json
COPY . .
COPY --from=build --chown=${APP_USER}:${APP_USER} /app .

USER ${APP_USER}:${APP_USER}
# We use single worker here, because gunicorn cannot handle multiple async eventlet
# workers. We need eventlet to support websockets.
ENTRYPOINT ["/bin/bash", "-c", "/venv/bin/gunicorn -w 3 --timeout 3600 rechol_user_section.wsgi:application -b 0.0.0.0:${APP_PORT} --preload"]


FROM nginx:1.25.2 AS nginx
SHELL ["/bin/sh", "-e", "-u", "-x", "-c"]

ARG NGINX_CONF

RUN rm /etc/nginx/conf.d/default.conf
COPY configs/${NGINX_CONF:-site.conf} /etc/nginx/templates/site.conf.template
COPY --from=build --chmod=777 --chown=root:root /app/static_files/ /home/rechol/static/
