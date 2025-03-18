#!/bin/bash
set -e

# Function to start supervisor with all services
start_all() {
  exec supervisord -c /etc/supervisor/conf.d/supervisord.conf
}

# Function to start just the main dockerforge CLI
start_cli() {
  exec python -m src.cli "$@"
}

# Function to start just the web service
start_web() {
  exec uvicorn src.web.api.main:app --host 0.0.0.0 --port 54321
}

# Parse argument and decide what to start
case "$1" in
  cli)
    shift
    start_cli "$@"
    ;;
  web)
    start_web
    ;;
  all|"")
    start_all
    ;;
  *)
    # Default to CLI with all arguments
    start_cli "$@"
    ;;
esac
