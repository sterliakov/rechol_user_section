#! /usr/bin/env bash

curlWithAuthHeader() {
  auth_params=()
  if [ -n "$CURL_AUTH_HEADER" ]; then
    auth_params+=('-H' "Authorization: $CURL_AUTH_HEADER")
  fi
  curl "${auth_params[@]}" -L "$@"
}

curlStatus() {
  curl_output="$1"
  if [ -z "$curl_output" ]; then
    # shellcheck disable=SC2016
    echo 'curlStatus: no $1 for curl_output' >&2
    return 1
  fi
  echo "$curl_output" | grep '^< HTTP/[0-9\.]* ' | tail -n 1 | awk '{print $3}'
}

assertCurlStatus() {
  expected_code="$1"
  curl_output="$2"
  status_code=$(curlStatus "$curl_output")
  if [[ "$status_code" != "$expected_code" ]]; then
    echo "curl returned http status code of '$status_code' instead of '$expected_code'" >&2
    echo "$curl_output" >&2
    return 1
  fi
}

repoUrl() {
  check_vars REPO_FQDN REPO_NAME
  echo "https://$REPO_FQDN/v2/$REPO_NAME"
}

check_vars() {
  var_names=("$@")
  for var_name in "${var_names[@]}"; do
    if [ -z "${!var_name}" ]; then
      echo >&2 "$var_name is unset."
      var_unset="true"
    fi
  done
  if [ -n "${var_unset:-}" ]; then
    exit 1
  fi
  return 0
}
