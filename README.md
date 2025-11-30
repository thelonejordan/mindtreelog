# MindTreeLog

A Django-based YouTube video collection manager with a modern, dark-themed UI.

## Prerequisites

Install the following tools:
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer
- [just](https://github.com/casey/just) - Command runner

## Setup

1. Clone the repository

2. Create environment file:
   ```shell
   cp env.example .env
   ```
   Edit `.env` and add your configuration (see Configuration section below)

3. Setup the project (creates venv, installs dependencies, and sets up pre-commit hooks):
   ```shell
   just setup
   ```

4. Run migrations:
   ```shell
   just migrate
   ```

5. Start the development server:
   ```shell
   just runserver
   ```

## Configuration

### Required Environment Variables

Create a `.env` file in the project root with the following variables:

```shell
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=true
DEV_MODE=true

# Twitter/X API (Optional - for full post details)
TWITTER_BEARER_TOKEN=your-bearer-token-here
```

### Twitter API Setup (Optional)

To fetch full tweet details (author name, text content), you need Twitter API credentials:

1. **Apply for Twitter Developer Account:**
   - Visit https://developer.twitter.com/
   - Sign up and create a new Project & App
   - Navigate to your App's "Keys and tokens" section

2. **Get Bearer Token:**
   - Generate a Bearer Token
   - Copy it to your `.env` file as `TWITTER_BEARER_TOKEN`

3. **API Tiers:**
   - **Free**: 1,500 tweets/month (sufficient for personal use)
   - **Basic**: $100/month, 10,000 tweets/month
   - **Pro**: $5,000/month, 1M tweets/month

**Note:** Without Twitter API credentials, posts will still be added but with placeholder text. You can edit them manually in the Django admin interface.

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

## VSCode Setup

This project includes VSCode configuration for debugging and development:

### Debugging

The project includes pre-configured debug configurations:

1. **Django: runserver** - Debug the Django development server
2. **Django: runserver (no reload)** - Debug without auto-reload (useful for debugging startup issues)
3. **Django: shell** - Debug in Django shell
4. **Django: migrate** - Debug migrations
5. **Python: Current File** - Debug the currently open Python file

To start debugging:
1. Open the Run and Debug panel (Ctrl/Cmd + Shift + D)
2. Select a configuration from the dropdown
3. Press F5 or click the green play button

### Recommended Extensions

VSCode will prompt you to install recommended extensions:
- **Python** - Python language support
- **Debugpy** - Python debugger
- **Pylance** - Fast Python language server
- **Ruff** - Fast Python linter and formatter
- **Django** - Django template support

### Settings

The project is configured to:
- Use the virtual environment at `.venv/bin/python`
- Format Python files with Ruff on save
- Auto-fix linting issues on save
- Organize imports on save
- Enable Django template syntax highlighting

## Features

- 📹 YouTube video collection management (`/list`)
- 𝕏 Twitter/X post collection management (`/xlist`)
- 🎨 Modern dark-themed UI
- 🔀 Toggle between card and list views
- ➕ Add content by pasting URLs
- 🔄 Auto-fetch metadata (titles, thumbnails, author info)
- 📱 Responsive design
- ⌨️ Keyboard shortcuts (Ctrl/Cmd + K to add, Escape to close)
- 💾 Persistent view preferences
- 🔍 Django admin interface for managing content
