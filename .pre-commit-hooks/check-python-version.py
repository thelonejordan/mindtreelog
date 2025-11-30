#!/usr/bin/env python3
"""Check Python version consistency across configuration files."""

import re
import sys
from pathlib import Path


def get_python_version_from_file(file_path: Path) -> str | None:
    """Extract Python version from .python-version file."""
    if not file_path.exists():
        return None
    content = file_path.read_text().strip()
    # Handle formats like "3.13" or "3.13.0"
    match = re.match(r"^(\d+\.\d+)", content)
    return match.group(1) if match else None


def get_python_version_from_pyproject(file_path: Path) -> str | None:
    """Extract Python version from pyproject.toml."""
    if not file_path.exists():
        return None
    content = file_path.read_text()
    # Match patterns like requires-python = ">=3.13"
    match = re.search(r'requires-python\s*=\s*">=(\d+\.\d+)"', content)
    return match.group(1) if match else None


def get_python_version_from_ruff(file_path: Path) -> str | None:
    """Extract Python version from ruff.toml."""
    if not file_path.exists():
        return None
    content = file_path.read_text()
    # Match patterns like target-version = "py313"
    match = re.search(r'target-version\s*=\s*"py(\d)(\d+)"', content)
    if match:
        return f"{match.group(1)}.{match.group(2)}"
    return None


def main() -> int:
    """Check Python version consistency."""
    repo_root = Path.cwd()

    python_version_file = repo_root / ".python-version"
    pyproject_file = repo_root / "pyproject.toml"
    ruff_file = repo_root / "ruff.toml"

    # Get versions from each file
    python_version = get_python_version_from_file(python_version_file)
    pyproject_version = get_python_version_from_pyproject(pyproject_file)
    ruff_version = get_python_version_from_ruff(ruff_file)

    versions = {
        ".python-version": python_version,
        "pyproject.toml": pyproject_version,
        "ruff.toml": ruff_version,
    }

    # Filter out None values
    valid_versions = {k: v for k, v in versions.items() if v is not None}

    if not valid_versions:
        print("❌ Could not find Python version in any configuration file")
        return 1

    # Check if all versions are the same
    unique_versions = set(valid_versions.values())

    if len(unique_versions) > 1:
        print("❌ Python version mismatch detected:")
        for file, version in valid_versions.items():
            print(f"  {file}: {version}")
        print("\n💡 All files should specify the same Python version.")
        return 1

    version = unique_versions.pop()
    print(f"✅ Python version is consistent across all files: {version}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
