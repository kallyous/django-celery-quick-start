#!/bin/bash

# Obtém diretório atual desse script
APP_HOME="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Activate the virtual environment
cd $APP_HOME
pipenv shell

# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)
exec $APP_HOME/.venv/bin/celery -A djangelery worker --loglevel=INFO &>logs/djangelery-worker.log
