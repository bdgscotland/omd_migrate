# Repository Badges

Once this repository is public on GitHub, you can replace the static badges in README.md with these dynamic ones:

## Dynamic Badges (for public repository)

```markdown
# Replace the static badges with these dynamic ones:

[![CI](https://github.com/bdgscotland/omd_migrate/actions/workflows/ci.yml/badge.svg)](https://github.com/bdgscotland/omd_migrate/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/bdgscotland/omd_migrate/branch/main/graph/badge.svg)](https://codecov.io/gh/bdgscotland/omd_migrate)
[![PyPI version](https://badge.fury.io/py/omd-migrate.svg)](https://badge.fury.io/py/omd-migrate)
[![Downloads](https://pepy.tech/badge/omd-migrate)](https://pepy.tech/project/omd-migrate)
[![GitHub stars](https://img.shields.io/github/stars/bdgscotland/omd_migrate.svg?style=social&label=Star)](https://github.com/bdgscotland/omd_migrate)
[![GitHub forks](https://img.shields.io/github/forks/bdgscotland/omd_migrate.svg?style=social&label=Fork)](https://github.com/bdgscotland/omd_migrate/fork)
[![GitHub issues](https://img.shields.io/github/issues/bdgscotland/omd_migrate.svg)](https://github.com/bdgscotland/omd_migrate/issues)
[![GitHub pull requests](https://img.shields.io/github/issues-pr/bdgscotland/omd_migrate.svg)](https://github.com/bdgscotland/omd_migrate/pulls)
[![Last commit](https://img.shields.io/github/last-commit/bdgscotland/omd_migrate.svg)](https://github.com/bdgscotland/omd_migrate/commits/main)
```

## Badge Categories

### Build & Quality
- CI/CD status from GitHub Actions
- Code coverage from Codecov
- Code quality from Code Climate or SonarCloud

### Package Info
- PyPI version (if published to PyPI)
- Python version compatibility
- License type

### Community
- GitHub stars and forks
- Download counts
- Issue and PR counts
- Last commit date

### Security
- Security score from Snyk
- Vulnerability status
- Dependency status

## Setup Instructions

### 1. Codecov Integration
1. Sign up at [codecov.io](https://codecov.io)
2. Connect your GitHub repository
3. Add the Codecov token to GitHub repository secrets as `CODECOV_TOKEN`

### 2. PyPI Publishing (Optional)
If you want to publish as a package:
1. Create `setup.py` or `pyproject.toml`
2. Publish to PyPI
3. Update badges with correct package name

### 3. Code Quality Services (Optional)
- **Code Climate**: [codeclimate.com](https://codeclimate.com)
- **SonarCloud**: [sonarcloud.io](https://sonarcloud.io)
- **Snyk**: [snyk.io](https://snyk.io)

## Example Badge Layout

```markdown
# OpenMetadata Migration Tool

<!-- Build and Quality -->
[![CI](https://github.com/bdgscotland/omd_migrate/workflows/CI/badge.svg)](https://github.com/bdgscotland/omd_migrate/actions)
[![codecov](https://codecov.io/gh/bdgscotland/omd_migrate/branch/main/graph/badge.svg)](https://codecov.io/gh/bdgscotland/omd_migrate)
[![Code Climate](https://api.codeclimate.com/v1/badges/HASH/maintainability)](https://codeclimate.com/github/bdgscotland/omd_migrate/maintainability)

<!-- Package Info -->
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PyPI version](https://badge.fury.io/py/omd-migrate.svg)](https://badge.fury.io/py/omd-migrate)

<!-- Community -->
[![GitHub stars](https://img.shields.io/github/stars/bdgscotland/omd_migrate.svg?style=social&label=Star)](https://github.com/bdgscotland/omd_migrate)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
```