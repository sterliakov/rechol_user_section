#!/usr/bin/env bash
set -eu

##
# `docker pull` from a repo and then `docker push` to another repo with just curl
# https://distribution.github.io/distribution/spec/api/
#
# Example usage:
#   source './helpers.sh'
#   PULL_CURL_AUTH_HEADER=... \
#     PULL_REPO_FQDN='public.ecr.aws' \
#     PULL_REPO_NAME='lambda/provided' \
#     PULL_IMAGE_TAG='al2-x86_64' \
#     PULL_DOWNLOAD_DIR_PATH='/path/to/download/image/contents' \
#     PUSH_CURL_AUTH_HEADER=... \
#     PUSH_REPO_FQDN='123456789012.dkr.ecr.us-east-1.amazonaws.com' \
#     PUSH_REPO_NAME='my-repo' \
#     PUSH_IMAGE_TAG='latest' \
#     ./pull_then_push.sh
##

dir_path() {
  # https://stackoverflow.com/a/43919044
  a="/$0"; a="${a%/*}"; a="${a:-.}"; a="${a##/}/"; BINDIR=$(cd "$a"; pwd)
  echo "$BINDIR"
}

SCRIPT_NAME="${0##*/}"  # https://stackoverflow.com/a/192699
DIR_PATH=$(dir_path)

. "$DIR_PATH/helpers.sh"


# Assert inputs
if [ -z ${PULL_CURL_AUTH_HEADER+x} ]; then
  echo >&2 "\$PULL_CURL_AUTH_HEADER is undefined. If no auth header required then set PULL_CURL_AUTH_HEADER=''"
  exit 1
fi

check_vars PULL_REPO_FQDN PULL_REPO_NAME PULL_IMAGE_TAG PULL_DOWNLOAD_DIR_PATH
check_vars PUSH_REPO_FQDN PUSH_REPO_NAME PUSH_IMAGE_TAG

if [ -z ${PUSH_CURL_AUTH_HEADER+z} ]; then
  echo "$SCRIPT_NAME: \$PUSH_CURL_AUTH_HEADER is undefined. If no auth header required then set PUSH_CURL_AUTH_HEADER=''" >&2
  exit 1
fi

# Pull image
export CURL_AUTH_HEADER="$PULL_CURL_AUTH_HEADER"
manifest_path=$(
  REPO_FQDN="$PULL_REPO_FQDN" \
  REPO_NAME="$PULL_REPO_NAME" \
  IMAGE_TAG="$PULL_IMAGE_TAG" \
  DOWNLOAD_DIR_PATH="$PULL_DOWNLOAD_DIR_PATH" \
  "$DIR_PATH/pull.sh"
)

# Push image
export CURL_AUTH_HEADER="$PUSH_CURL_AUTH_HEADER"
REPO_FQDN="$PUSH_REPO_FQDN" \
REPO_NAME="$PUSH_REPO_NAME" \
IMAGE_TAG="$PUSH_IMAGE_TAG" \
LAYER_PATHS=$(find "$PULL_DOWNLOAD_DIR_PATH/layers" -type f) \
CONFIG_PATH="$PULL_DOWNLOAD_DIR_PATH/config.json" \
MANIFEST_PATH="$manifest_path" \
  "$DIR_PATH/push.sh"

# Clean up
unset CURL_AUTH_HEADER
rm -rf "$PULL_DOWNLOAD_DIR_PATH"
