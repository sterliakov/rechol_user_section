ARG APP_USER=rechol

FROM python:3.12-slim AS build
SHELL ["/bin/bash", "-e", "-u", "-x", "-o", "pipefail", "-c"]

ARG DEBIAN_FRONTEND=noninteractive

COPY uv.lock pyproject.toml /
ARG UV_FLAGS=--no-dev
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
# hadolint ignore=DL3008
RUN --mount=type=cache,target=/root/.cache \
    apt-get -qq update \
    && apt-get -qq install -y --no-install-recommends gettext \
    && rm -rf /var/lib/apt/lists/* \
    && uv sync ${UV_FLAGS} --locked --no-install-project \
    && uv pip install --no-cache-dir 'setuptools >= 69.1.1'

WORKDIR /app
ENV PATH="/.venv/bin:$PATH"

COPY manage.py ./
COPY rechol_user_section/ ./rechol_user_section/
COPY users/__init__.py ./users/__init__.py

COPY patches/ ./patches/
COPY users/locale ./users/locale
RUN ENVIRONMENT=build ./manage.py compilemessages

FROM python:3.12-slim AS base
SHELL ["/bin/bash", "-e", "-u", "-x", "-o", "pipefail", "-c"]

ARG APP_HOME=/home/rechol
ARG DEBIAN_FRONTEND=noninteractive

# hadolint ignore=DL3008
RUN apt-get -qq update \
    && apt-get -qq upgrade -y \
    && apt-get -qq install -y --no-install-recommends libpcre3 mime-support \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir /opt/extensions/ && chmod 755 /root

WORKDIR ${APP_HOME}
COPY --from=build /.venv /.venv
ENV PATH="/.venv/bin:$PATH"
# Patch
COPY --from=build /app/patches/locale_ru/ /.venv/lib/python3.12/site-packages/django/conf/locale/ru/LC_MESSAGES
COPY . .
COPY --from=build /app .

FROM base AS deploy
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONFAULTHANDLER=1
ENV PYTHONUNBUFFERED=1

ARG CLUSTER_ID=d6a94efc-e0ce-4829-9fbe-42618ad3cdf6
ADD --chmod=444 https://cockroachlabs.cloud/clusters/${CLUSTER_ID}/cert /certs/ca.crt
COPY entrypoint.sh /entrypoint.sh
ADD --chmod=755 https://github.com/aws/aws-lambda-runtime-interface-emulator/releases/latest/download/aws-lambda-rie /usr/local/bin/aws-lambda-rie
ENTRYPOINT [ "/entrypoint.sh" ]
CMD [ "rechol_user_section.aws_lambda.handler" ]

FROM public.ecr.aws/docker/library/node:20.18-alpine AS npm
WORKDIR /app
RUN npm i bootstrap@4.6.2

FROM python:3.12-slim AS get-sass
WORKDIR /sass
ADD https://github.com/sass/dart-sass/releases/download/1.80.3/dart-sass-1.80.3-linux-x64.tar.gz /sass/archive.tar.gz
RUN tar xzf ./archive.tar.gz

FROM base AS staticfiles
COPY --from=npm /app/node_modules ./node_modules
COPY --from=get-sass /sass/dart-sass/ /tmp/sass/
RUN mkdir static_files
ENV SASS_EXECUTABLE=/tmp/sass/sass
ENV ENVIRONMENT=build
ENTRYPOINT ["./manage.py"]

FROM nginx:1.25.2 AS nginx
SHELL ["/bin/sh", "-e", "-u", "-x", "-c"]
ARG NGINX_CONF=site.conf
RUN rm /etc/nginx/conf.d/default.conf
COPY configs/${NGINX_CONF} /etc/nginx/templates/site.conf.template
