# Contributing to OpenMetadata Migration Tool

Thank you for your interest in contributing to the OpenMetadata Migration Tool! We welcome contributions from the community.

## 📋 Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Pull Request Process](#pull-request-process)
- [Code Style Guidelines](#code-style-guidelines)
- [Testing](#testing)
- [Documentation](#documentation)

## Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code:

- Be respectful and inclusive
- Focus on constructive feedback
- Help create a welcoming environment for all contributors
- Respect differing viewpoints and experiences

## Getting Started

### Ways to Contribute

- 🐛 **Bug Reports**: Report bugs using GitHub issues
- 💡 **Feature Requests**: Suggest new features or improvements
- 📖 **Documentation**: Improve documentation and examples
- 🧪 **Testing**: Add test cases and improve coverage
- 🔧 **Code**: Fix bugs or implement new features

### Before You Start

1. Check existing [issues](../../issues) and [pull requests](../../pulls)
2. For large changes, create an issue first to discuss the approach
3. Make sure your contribution aligns with the project goals

## Development Setup

### Prerequisites

- Python 3.9+ 
- Git
- Virtual environment tool (venv, conda, etc.)

### Setup Instructions

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/your-username/omd_migrate.git
   cd omd_migrate
   ```

2. **Set up development environment**
   ```bash
   # Option A: Use automated setup
   ./setup.sh
   
   # Option B: Manual setup
   python -m venv omd_venv
   source omd_venv/bin/activate  # On Windows: omd_venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

3. **Verify setup**
   ```bash
   make test
   make lint
   ```

## Making Changes

### Branching Strategy

- Create feature branches from `main`
- Use descriptive branch names: `feat/add-export-filtering` or `fix/import-error-handling`
- Keep branches focused on a single feature or fix

### Development Workflow

1. **Create a branch**
   ```bash
   git checkout -b feat/your-feature-name
   ```

2. **Make your changes**
   - Write clear, concise code
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**
   ```bash
   make test          # Run test suite
   make lint          # Check code quality
   make all-checks    # Run all quality checks
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add new export filtering capability"
   ```

   Follow [Conventional Commits](https://www.conventionalcommits.org/) format:
   - `feat:` for new features
   - `fix:` for bug fixes
   - `docs:` for documentation changes
   - `test:` for test improvements
   - `refactor:` for code refactoring
   - `chore:` for maintenance tasks

## Pull Request Process

### Before Submitting

- [ ] Code follows the project style guidelines
- [ ] Tests pass locally (`make test`)
- [ ] Code is properly linted (`make lint`)
- [ ] Documentation is updated for new features
- [ ] Commit messages follow conventional format
- [ ] Branch is up to date with main

### Submitting a PR

1. **Push your branch**
   ```bash
   git push origin feat/your-feature-name
   ```

2. **Create a Pull Request**
   - Use the provided PR template
   - Include a clear description of changes
   - Reference related issues
   - Add screenshots for UI changes

3. **Address Review Feedback**
   - Respond to comments promptly
   - Make requested changes
   - Update tests and documentation as needed

### PR Requirements

All PRs must pass:
- ✅ Automated tests (Python 3.9, 3.10, 3.11)
- ✅ Code quality checks (black, flake8, mypy)
- ✅ Security scans (bandit, trivy)
- ✅ Documentation validation
- ✅ Manual review by maintainers

## Code Style Guidelines

### Python Code Style

We use automated tools to enforce code style:

- **Black**: Code formatting
- **flake8**: Linting and style checking
- **mypy**: Type checking
- **isort**: Import sorting

### Configuration Files

- **YAML**: 2-space indentation
- **JSON**: 2-space indentation
- **Markdown**: Follow standard markdown formatting

### Best Practices

- Use descriptive variable and function names
- Add type hints for function parameters and return values
- Write docstrings for classes and functions
- Keep functions small and focused
- Follow DRY (Don't Repeat Yourself) principles

### Example Code Style

```python
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class ExampleClass:
    """Example class demonstrating code style."""
    
    def __init__(self, config: Dict[str, str]) -> None:
        self.config = config
        
    def process_entities(self, entities: List[str]) -> Optional[Dict[str, int]]:
        """Process a list of entities and return counts.
        
        Args:
            entities: List of entity names to process
            
        Returns:
            Dictionary mapping entity types to counts, or None if error
        """
        try:
            # Implementation here
            return {"processed": len(entities)}
        except Exception as e:
            logger.error(f"Failed to process entities: {e}")
            return None
```

## Testing

### Test Structure

- Unit tests in `test_migration.py`
- Integration tests for CLI commands
- Mock external dependencies (OpenMetadata API)

### Writing Tests

```python
def test_export_functionality():
    """Test export functionality with mock data."""
    # Arrange
    mock_config = {"server_url": "http://test.com"}
    
    # Act
    result = export_function(mock_config)
    
    # Assert
    assert result is not None
    assert "success" in result
```

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
pytest --cov=. test_migration.py

# Run specific test
pytest test_migration.py::TestExport::test_specific_function
```

## Documentation

### Documentation Standards

- Keep README.md up to date
- Document all public functions and classes
- Provide usage examples
- Update configuration documentation

### Documentation Types

- **Code Comments**: Explain complex logic
- **Docstrings**: Document function/class purpose and usage
- **README**: High-level project documentation
- **Examples**: Practical usage examples

## Getting Help

### Resources

- [Project README](README.md) - Basic usage and setup
- [GitHub Issues](../../issues) - Bug reports and feature requests
- [GitHub Discussions](../../discussions) - General questions and ideas

### Contact

- Create an issue for bugs or feature requests
- Use discussions for questions and ideas
- Tag maintainers for urgent issues

## Recognition

Contributors will be recognized in:
- GitHub contributors page
- Release notes for significant contributions
- Project documentation

Thank you for contributing to the OpenMetadata Migration Tool! 🎉