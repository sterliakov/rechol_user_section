FROM public.ecr.aws/docker/library/node:20.18-alpine AS npm
WORKDIR /app
RUN npm i bootstrap@4.6.2

FROM python:3.12-slim AS get-sass
WORKDIR /sass
ADD https://github.com/sass/dart-sass/releases/download/1.80.3/dart-sass-1.80.3-linux-x64.tar.gz /sass/archive.tar.gz
RUN tar xzf ./archive.tar.gz

FROM python:3.12-slim AS build
SHELL ["/bin/bash", "-e", "-u", "-x", "-o", "pipefail", "-c"]

ARG REQUIREMENTS_FILE=requirements.txt
ENV DEBIAN_FRONTEND=noninteractive
ENV COMPRESSOR_CACHE=filesystem
ENV DJANGO_SECRET_KEY=1
ENV USER_MODEL="auth.User"

COPY uv.lock pyproject.toml /
ARG UV_FLAGS=--no-dev
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
# hadolint ignore=DL3008
RUN --mount=type=cache,target=/root/.cache \
    apt-get -qq update \
    && apt-get -qq install -y --no-install-recommends gettext \
    && rm -rf /var/lib/apt/lists/* \
    && uv sync ${UV_FLAGS} --locked --no-install-project \
    && uv pip install --no-cache-dir 'setuptools >= 69.1.1' 'gunicorn ~= 21.2.0'

WORKDIR /app
ENV PATH="/.venv/bin:$PATH"

COPY manage.py ./
COPY rechol_user_section/ ./rechol_user_section/
COPY users/__init__.py ./users/__init__.py

COPY patches/ ./patches/
COPY users/locale ./users/locale
RUN ./manage.py compilemessages

FROM python:3.12-slim AS base
SHELL ["/bin/bash", "-e", "-u", "-x", "-o", "pipefail", "-c"]

ARG APP_USER=rechol
ARG APP_HOME=/home/rechol
ENV DEBIAN_FRONTEND=noninteractive

# hadolint ignore=DL3008
RUN groupadd -r ${APP_USER} && useradd --no-log-init -r -g ${APP_USER} ${APP_USER} \
    && apt-get -qq update \
    && apt-get -qq upgrade -y \
    && apt-get -qq install -y --no-install-recommends libpcre3 mime-support \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /var/www/rechol_user_section/media/ \
    && chown -R "${APP_USER}:${APP_USER}" /var/www/rechol_user_section/media/ \
    && mkdir -p /home/${APP_USER}/static_files \
    && chown -R "${APP_USER}:${APP_USER}" /home/${APP_USER}/static_files

WORKDIR ${APP_HOME}
COPY --from=build /.venv /.venv
ENV PATH="/.venv/bin:$PATH"
# Patch
COPY --from=build --chown=${APP_USER}:${APP_USER} /app/patches/locale_ru/ /.venv/lib/python3.12/site-packages/django/conf/locale/ru/LC_MESSAGES
COPY . .
COPY --from=build --chown=${APP_USER}:${APP_USER} /app .

# FROM base AS staticfiles
COPY --from=npm /app/node_modules ./node_modules
COPY --from=get-sass /sass/dart-sass/ /tmp/sass/
ENV SASS_EXECUTABLE=/tmp/sass/sass
# ENTRYPOINT ["manage.py"]

FROM base AS deploy
USER ${APP_USER}:${APP_USER}
# We use single worker here, because gunicorn cannot handle multiple async eventlet
# workers. We need eventlet to support websockets.
ENTRYPOINT ["/bin/bash", "-c", "/.venv/bin/gunicorn -w 3 --timeout 3600 rechol_user_section.wsgi:application -b 0.0.0.0:${APP_PORT} --preload"]


FROM nginx:1.25.2 AS nginx
SHELL ["/bin/sh", "-e", "-u", "-x", "-c"]
ARG NGINX_CONF=site.conf
RUN rm /etc/nginx/conf.d/default.conf
COPY configs/${NGINX_CONF} /etc/nginx/templates/site.conf.template
