set dotenv-load

# Default recipe - show available commands
[private]
list:
    #!/usr/bin/env bash
    set -euo pipefail  # https://github.com/casey/just#safer-bash-shebang-recipes

    just --list --unsorted --justfile {{justfile()}}

default:
    @just list


python := ".venv/bin/python"
pip := ".venv/bin/pip"

django_help:
    {{python}} manage.py help

reset_db:
    {{python}} manage.py reset_db --close-sessions --no-input

flush_db:
    {{python}} manage.py flush --no-input

migrate:
    {{python}} manage.py migrate

reset: reset_db migrate

runserver PORT='8000':
    {{python}} manage.py runserver {{PORT}}

show_urls:
    {{python}} manage.py show_urls

shell:
    {{python}} manage.py shell

dbshell:
    {{python}} manage.py dbshell

runscript TITLE:
    {{python}} manage.py runscript {{TITLE}}

lint:
    git ls-files '*.py' | xargs {{python}} -m ruff check --fix

format:
    git ls-files '*.py' | xargs {{python}} -m ruff format
