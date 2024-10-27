#!/usr/bin/env bash
set -eu

##
# `docker push` to repo with just curl
# https://distribution.github.io/distribution/spec/api/
# https://stackoverflow.com/a/59901770
#
# See ./pull_then_push.sh for example usage.
##


dir_path() {
  # https://stackoverflow.com/a/43919044
  a="/$0"; a="${a%/*}"; a="${a:-.}"; a="${a##/}/"; BINDIR=$(cd "$a"; pwd)
  echo "$BINDIR"
}

SCRIPT_NAME="${0##*/}"  # https://stackoverflow.com/a/192699
DIR_PATH=$(dir_path)

. "$DIR_PATH/helpers.sh"


check_vars REPO_FQDN REPO_NAME IMAGE_TAG LAYER_PATHS CONFIG_PATH

echo "$LAYER_PATHS" | while read -r layer_path ; do
  if [[ ! -f "$layer_path" ]]; then
    echo "$SCRIPT_NAME: no file exists at layer_path of '$layer_path'" >&2
    exit 1
  fi
done

if [[ ! -f "$CONFIG_PATH" ]]; then
  echo "$SCRIPT_NAME: no file exists at CONFIG_PATH='$CONFIG_PATH'" >&2
  exit 1
fi


fileSize() {
  file_path="$1"
  check_vars file_path
  echo $(( $(wc -c < "$file_path") ))
}

fileDigest() {
  file_path="$1"
  check_vars file_path
  echo "sha256:$(sha256sum "$file_path" | cut -d ' ' -f1)"
}

initiateUpload() {
  check_vars REPO_URL

  echo 'initiateUpload: starting' >&2

  curl_output=$(
    curlWithAuthHeader -X POST -siL -v \
    -H "Connection: close" \
    "$REPO_URL/blobs/uploads" \
    2>&1
  )
  assertCurlStatus 202 "$curl_output"

  location=$(
    echo "$curl_output" \
    | grep Location \
    | sed '2q;d' \
    | cut -d: -f2- \
    | tr -d ' ' \
    | tr -d '\r'
  )
  if [[ -z "$location" ]]; then
    echo 'initiateUpload: Failed to parse Location from curl_output' >&2
    return 1
  fi

  echo 'initiateUpload: complete' >&2
  echo "$location"
}

patchLayer() {
  echo 'patchLayer: starting' >&2

  curl_output=$(
    curlWithAuthHeader -X PATCH -v \
    -H "Content-Type: application/octet-stream" \
    -H "Content-Length: ${file_size:?missing file_size}" \
    -H "Connection: close" \
    --data-binary @"${file_path:?missing file_path}" \
    "${target_location:?missing target_location}" \
    2>&1
  )
  assertCurlStatus 201 "$curl_output"

  location=$(
    echo "$curl_output" \
    | grep 'Location' \
    | cut -d: -f2- \
    | tr -d ' ' \
    | tr -d '\r'
  )
  if [[ -z "$location" ]]; then
    echo 'patchLayer: Failed to parse location from curl_output' >&2
    return 1
  fi

  echo 'patchLayer: complete' >&2
  echo "$location"
}

putLayer() {
  echo 'putLayer: starting' >&2

  curl_output=$(
    curlWithAuthHeader -X PUT -v \
    -H "Content-Type: application/octet-stream" \
    -H "Content-Length: 0" \
    -H "Connection: close" \
    "${target_location:?missing target_location}?digest=${file_digest:?missing file_digest}" \
    2>&1
  )
  assertCurlStatus 201 "$curl_output"

  echo 'putLayer: complete' >&2
}

uploadManifest() {
  manifest_path="$1"
  echo "uploadManifest: starting '$manifest_path'" >&2
  check_vars REPO_URL IMAGE_TAG manifest_path

  size=$(( $(fileSize "$manifest_path") - 1))

  curl_output=$(
    curlWithAuthHeader -X PUT -v \
    -H "Content-Type: application/vnd.docker.distribution.manifest.v2+json" \
    -H "Content-Length: $size" \
    -H "Connection: close" \
    -d "$(cat "$manifest_path")" \
    "$REPO_URL/manifests/$IMAGE_TAG" \
    2>&1
  )
  assertCurlStatus 201 "$curl_output"

  echo "uploadManifest: complete '$manifest_path'" >&2
}

uploadImage() {
  check_vars CONFIG_PATH LAYER_PATHS MANIFEST_PATH

  echo "uploadImage: starting config at '$CONFIG_PATH'" >&2
  config_size=$(fileSize "$CONFIG_PATH")
  config_digest=$(fileDigest "$CONFIG_PATH")
  patch_location=$(initiateUpload)
  put_location=$(
    file_path="$CONFIG_PATH" \
    file_size="$config_size" \
    target_location="$patch_location" \
    patchLayer
  )
  file_digest="$config_digest" target_location="$put_location" putLayer
  echo "uploadImage: complete config at '$CONFIG_PATH'" >&2

  echo 'uploadImage: starting layers' >&2
  while read -r layer_path ; do
    echo "uploadImage: starting layer at '$layer_path'" >&2
    layer_size=$(fileSize "$layer_path")
    layer_digest=$(fileDigest "$layer_path")
    patch_location=$(initiateUpload)
    put_location=$(
      file_path="$layer_path" \
      file_size="$layer_size" \
      target_location="$patch_location" \
      patchLayer
    )
    file_digest="$layer_digest" target_location="$put_location" putLayer
    echo "uploadImage: complete layer at '$layer_path'" >&2
  done <<< "$LAYER_PATHS"
  echo 'uploadImage: complete layers' >&2

  uploadManifest "${MANIFEST_PATH:?MANIFEST_PATH not provided}"
  echo 'uploadImage: complete manifest' >&2
}

REPO_URL=$(REPO_FQDN="$REPO_FQDN" REPO_NAME="$REPO_NAME" repoUrl)
uploadImage
