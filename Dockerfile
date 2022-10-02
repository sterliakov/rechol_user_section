FROM python:3.10-slim
SHELL ["/bin/bash", "-e", "-u", "-x", "-o", "pipefail", "-c"]

ARG APP_USER
ARG SERVER_ADMIN
ARG SERVER_NAME
ARG DEBIAN_FRONTEND=noninteractive
ENV DJANGO_SETTINGS_MODULE=rechol_user_section.settings

RUN groupadd -r ${APP_USER} && useradd --no-log-init -r -g ${APP_USER} ${APP_USER}

# hadolint ignore=SC2086
RUN RUN_DEPS=" \
    libpcre3 \
    mime-support \
    postgresql-client \
    apache2 \
    libxml2-dev libxmlsec1-openssl \
    " && \
    apt-get update && apt-get install -y --no-install-recommends $RUN_DEPS && \
    apt-get upgrade -y && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /requirements.txt
COPY ./site.conf /etc/apache2/sites-available/000-default.conf
COPY ./certs/ /etc/letsencrypt/live/${SERVER_NAME}/

# hadolint ignore=SC2086
RUN BUILD_DEPS="build-essential libpcre3-dev libpq-dev git pkg-config apache2-dev libxmlsec1-dev" && \
    apt-get update && apt-get install -y --no-install-recommends $BUILD_DEPS && \
    pip install -U --no-cache-dir pip setuptools wheel && \
    pip install -U --no-cache-dir mod-wsgi && \
    pip install --no-cache-dir -r /requirements.txt && \
    apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false $BUILD_DEPS && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /var/log/apache2 && chown -R ${APP_USER} /var/log/apache2/ && chmod -R 700 /var/log/apache2/ && \
    mkdir -p /var/run/apache2 && chown -R ${APP_USER} /var/run/apache2/ && chmod -R 700 /var/run/apache2/ && \
    mkdir -p /var/log/rechol_user_section && chown -R ${APP_USER} /var/log/rechol_user_section/ && chmod -R 700 /var/log/rechol_user_section/ && \
    mkdir -p /var/run/rechol_user_section && chown -R ${APP_USER} /var/run/rechol_user_section/ && chmod -R 700 /var/run/rechol_user_section/ && \
    mkdir -p /var/www/rechol_user_section/media/ && chown -R ${APP_USER} /var/www/rechol_user_section/media/ && chmod -R 700 /var/www/rechol_user_section/media/

RUN printf 'export APP_USER=%s\nexport SERVER_ADMIN=%s\nexport SERVER_NAME=%s' "$APP_USER" "$SERVER_ADMIN" "$SERVER_NAME" >> /etc/apache2/envvars
RUN /usr/local/bin/mod_wsgi-express install-module | tee /etc/apache2/mods-available/wsgi_express.load /etc/apache2/mods-available/wsgi_express.conf
RUN a2enmod wsgi_express ssl proxy proxy_http proxy_wstunnel
# This affects /var/lock permissions, so required before user change.
# hadolint ignore=DL3001
RUN service apache2 start

COPY ./rechol_user_section/ /var/www/html/rechol_user_section
WORKDIR /var/www/html/rechol_user_section

RUN find . /usr/local/lib -name migrations -type d -exec chown -R ${APP_USER} {} \; && \
    find . /usr/local/lib -name migrations -type d -exec chmod -R 700 {} \; && \
    chown -R ${APP_USER} . && chmod -R 700 .

USER ${APP_USER}:${APP_USER}
ENTRYPOINT ["./entrypoint.sh"]
