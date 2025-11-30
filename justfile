set dotenv-load

# Default recipe - show available commands
[private]
list:
    #!/usr/bin/env bash
    set -euo pipefail  # https://github.com/casey/just#safer-bash-shebang-recipes

    just --list --unsorted --justfile {{justfile()}}

# Show all available commands
default:
    @just list


python := ".venv/bin/python"
pip := ".venv/bin/pip"

# Create virtual environment
venv:
    uv venv

# Sync dependencies from lock file
sync:
    uv sync

# Setup project: create venv, sync dependencies, install pre-commit hooks
setup: venv sync precommit-install

# Show all available Django management commands
django_help:
    {{python}} manage.py help

# Reset database (drops and recreates all tables)
reset_db:
    {{python}} manage.py reset_db --close-sessions --no-input

# Flush database (removes all data but keeps schema)
flush_db:
    {{python}} manage.py flush --no-input

# Run database migrations
migrate:
    {{python}} manage.py migrate

# Reset database and run migrations
reset: reset_db migrate

# Start Django development server on specified port (default: 8000)
runserver PORT='8000':
    {{python}} manage.py runserver {{PORT}}

# Display all registered URLs
show_urls:
    {{python}} manage.py show_urls

# Open Django interactive shell
shell:
    {{python}} manage.py shell

# Open database shell
dbshell:
    {{python}} manage.py dbshell

# Run a custom script using django-extensions
runscript TITLE:
    {{python}} manage.py runscript {{TITLE}}

# Lint tracked Python files with ruff (auto-fix enabled)
lint:
    git ls-files '*.py' | xargs {{python}} -m ruff check --fix

# Lint all Python files with ruff (auto-fix enabled)
lint-all:
    {{python}} -m ruff check --fix .

# Format tracked Python files with ruff
format:
    git ls-files '*.py' | xargs {{python}} -m ruff format

# Format all Python files with ruff
format-all:
    {{python}} -m ruff format .

# Install pre-commit git hooks
precommit-install:
    {{python}} -m pre_commit install

# Run pre-commit hooks on staged files
precommit:
    {{python}} -m pre_commit run

# Run pre-commit hooks on all files
precommit-all:
    {{python}} -m pre_commit run --all-files

# Update pre-commit hook versions
precommit-update:
    {{python}} -m pre_commit autoupdate
