#!/usr/bin/env bash

# Taken for LSSTTS Dockefile
pid=0

# SIGTERM-handler
term_handler() {
  if [ $pid -ne 0 ]; then
    kill -SIGTERM "$pid"
    wait "$pid"
  fi
  exit 143; # 128 + 15 -- SIGTERM
}

# setup handlers
# on callback, kill the last background process and execute term_handler
trap 'kill ${!}; term_handler' SIGTERM

echo "Exporting environment for broker_files"
export PYTHONPATH=${PYTHONPATH}:${HOME}/broker_files
export PATH=${PATH}:${HOME}/broker_files

echo "Starting conda env from: ${MINICONDA_PATH}"
. ${MINICONDA_PATH}/bin/activate base

args=("$@")
exec "${args[@]}"
