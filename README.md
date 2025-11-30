# MindTreeLog

A Django-based YouTube video collection manager with a modern, dark-themed UI.

## Prerequisites

Install the following tools:
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer
- [just](https://github.com/casey/just) - Command runner

## Setup

1. Clone the repository
2. Setup the project (creates venv, installs dependencies, and sets up pre-commit hooks):
   ```shell
   just setup
   ```

3. Run migrations:
   ```shell
   just migrate
   ```

4. Start the development server:
   ```shell
   just runserver
   ```

## Development

### Environment Management

```shell
# Create virtual environment
just venv

# Sync dependencies from lock file
just sync

# Complete setup (venv + sync + pre-commit install)
just setup
```

### Pre-commit Commands

Pre-commit hooks run automatically on every commit. You can also run them manually:

```shell
# Run pre-commit on all files
just precommit-all

# Run pre-commit on staged files only
just precommit

# Update pre-commit hooks
just precommit-update
```

### Pre-commit Hooks

The project uses pre-commit hooks to maintain code quality and consistency. These hooks run automatically before each commit:

#### Custom Checks
- **Python version consistency** - Ensures `.python-version`, `pyproject.toml`, and `ruff.toml` all specify the same Python version
- **uv.lock sync** - Verifies that `uv.lock` is in sync with `pyproject.toml` dependencies

#### Code Quality
- **Ruff linting** - Fast Python linter with auto-fix enabled
- **Ruff formatting** - Consistent Python code formatting

#### File Quality
- **Trailing whitespace** - Automatically removes trailing whitespace
- **End of file fixer** - Ensures files end with exactly one newline
- **Mixed line ending** - Normalizes line endings across files

#### Configuration Validation
- **YAML validation** - Checks YAML syntax
- **TOML validation** - Checks TOML syntax

#### Safety Checks
- **Large file detection** - Prevents accidental commits of large files
- **Merge conflict detection** - Catches unresolved merge conflict markers

All hooks run automatically on commit, but can also be run manually using the commands above.

### Linting & Formatting

```shell
# Lint tracked Python files (auto-fix enabled)
just lint

# Lint all Python files (auto-fix enabled)
just lint-all

# Format tracked Python files
just format

# Format all Python files
just format-all
```

### Database Commands

```shell
# Run migrations
just migrate

# Reset database
just reset_db

# Flush database
just flush_db

# Reset and migrate
just reset
```

### Other Commands

```shell
# Django shell
just shell

# Database shell
just dbshell

# Show all URLs
just show_urls

# View all available commands
just
```

## Features

- 📹 YouTube video collection management
- 🎨 Modern dark-themed UI
- 🔀 Toggle between card and list views
- ➕ Add videos by pasting YouTube URLs
- 🔄 Auto-fetch video titles and thumbnails
- 📱 Responsive design
