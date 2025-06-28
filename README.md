# OpenMetadata Migration Tool

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![OpenMetadata SDK](https://img.shields.io/badge/OpenMetadata%20SDK-1.8.0+-orange.svg)](https://pypi.org/project/openmetadata-ingestion/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

[![Code Quality](https://img.shields.io/badge/code%20quality-black%20%7C%20flake8%20%7C%20mypy-blue.svg)](https://github.com/psf/black)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-green.svg)](.github/workflows/ci.yml)
[![Security](https://img.shields.io/badge/security-bandit%20%7C%20trivy-red.svg)](https://github.com/PyCQA/bandit)
[![Testing](https://img.shields.io/badge/testing-pytest%20%7C%20coverage-blue.svg)](test_migration.py)

A flexible, customizable Python tool for exporting and importing OpenMetadata entities. Supports full backups, selective exports, and cross-instance migrations with clear NDJSON output format.

## Features

- **OpenMetadata SDK Integration**: Uses official OpenMetadata Python SDK for robust API interaction
- **Full Export/Import**: Backup and restore complete OpenMetadata instances  
- **Selective Export**: Export specific entity types with `--entities` flag
- **Round-Trip Tested**: Verified export → import → validation workflow with real data
- **Relationship-Aware**: Maintains links between domains, data products, and assets
- **Flexible Configuration**: YAML config with environment variable overrides
- **Rich Console Output**: Beautiful progress indicators and informative logging
- **NDJSON Format**: Human-readable, editable export format
- **Version Flexible**: Configurable OpenMetadata SDK version support (defaults to 1.8.0+)

## Quick Start

### 1. Installation

**Option A: Automated Setup (Recommended)**
```bash
git clone <repository>
cd omd_migrate
./setup.sh
```

**Option B: Manual Installation**
```bash
git clone <repository>
cd omd_migrate
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Note**: The setup.sh script creates a virtual environment (`omd_venv`) and installs all dependencies automatically.

### 2. Configuration

The tool uses both `config.yaml` and `.env` files for configuration:

**Option A: Use .env file (recommended for credentials)**
```bash
cp .env.example .env
# Edit .env with your OpenMetadata server details
```

**Option B: Edit config.yaml directly**
```bash
# Edit config.yaml with your server URL and JWT token
```

### 3. Export Data

```bash
# Export all entities (based on config.yaml settings)
python export.py

# Selective export of specific entity types
python export.py --entities data_products --entities domains

# Clear previous exports before starting
python export.py --clear

# Export to custom directory
python export.py --output-dir /path/to/backup

# Combine options for targeted exports
python export.py --clear --entities data_products --entities domains --output-dir /backup/domains-only
```

### 4. Import Data

```bash
# Import all entities
python import.py

# Import from custom directory
python import.py --input-dir /path/to/backup

# Import specific entity type only
python import.py --entity-type domains

# Dry run (see what would be imported)
python import.py --dry-run
```

## Configuration

### Environment Variables (.env)

```bash
# Server Configuration
OPENMETADATA_SERVER_URL=http://your-openmetadata-server:8585/api
OPENMETADATA_JWT_TOKEN=your_jwt_token_here

# Export Configuration
EXPORT_OUTPUT_DIR=./exports
EXPORT_BATCH_SIZE=100
EXPORT_INCLUDE_DELETED=false

# Import Configuration
IMPORT_INPUT_DIR=./exports
IMPORT_UPDATE_EXISTING=true
IMPORT_SKIP_ON_ERROR=true

# Logging
LOG_LEVEL=INFO
```

### Selective Export

Configure selective exports in `config.yaml`:

```yaml
export:
  selective:
    # Export specific domains by name
    domains: ["Finance", "Marketing"]
    
    # Only export data products linked to specified domains
    linked_data_products_only: true
    
    # Only export assets (tables, topics, etc.) linked to domains/data products
    linked_assets_only: true
```

### Entity Types

Supported entities for export (use with `--entities` flag):

**Core Entities:**
- `domains` - Business domains and subdomains
- `data_products` - Data products with domain relationships  
- `teams` - Teams and users
- `users` - Individual users
- `policies` - Access policies

**Knowledge Management:**
- `glossaries` - Business glossaries
- `glossary_terms` - Glossary terms

**Data Assets:**
- `databases` - Database services and databases
- `database_schemas` - Database schemas  
- `tables` - Data tables with lineage

**Additional Entity Types** (available via config.yaml):
- `topics` - Kafka topics and streams
- `dashboards` - BI dashboards
- `charts` - Dashboard charts
- `pipelines` - Data pipelines
- `ml_models` - Machine learning models
- `containers` - Data containers
- `stored_procedures` - Database procedures
- `dashboard_data_models` - Dashboard data models
- `search_indexes` - Search indexes

Example usage:
```bash
# Export core entities only
python export.py --entities domains --entities data_products --entities teams

# Export data assets
python export.py --entities databases --entities tables
```

## Examples

### Full Backup and Restore

```bash
# 1. Export everything from source instance
python export.py --config source-config.yaml --output-dir backup-2024-01-15

# 2. Import to target instance
python import.py --config target-config.yaml --input-dir backup-2024-01-15
```

### Selective Entity Export

Use command-line flags for targeted exports:

```bash
# Export only domains and data products
python export.py --clear --entities domains --entities data_products

# Export specific entities to custom location  
python export.py --entities users --entities teams --output-dir /backup/identity

# Clear and export tables only
python export.py --clear --entities tables
```

### Domain-Specific Migration

Configure selective export in `config.yaml`:
```yaml
export:
  selective:
    domains: ["Data Science", "Analytics"]
    linked_data_products_only: true
    linked_assets_only: true
```

Then export and import:
```bash
python export.py  # Exports only Data Science and Analytics domains + linked entities
python import.py --config target-config.yaml
```

### Cross-Instance Migration

```bash
# Export from production
OPENMETADATA_SERVER_URL=https://prod.your-company.com python export.py

# Import to staging  
OPENMETADATA_SERVER_URL=https://staging.your-company.com python import.py
```

## Output Format

Exports are saved as NDJSON files (one JSON object per line):

```
exports/
├── domains.ndjson              # Business domains
├── data_products.ndjson        # Data products
├── teams.ndjson                # Teams and users
├── tables.ndjson               # Data tables
├── topics.ndjson               # Kafka topics
└── export_summary.json         # Export metadata
```

Each NDJSON file can be:
- Viewed and edited with any text editor
- Processed with command-line tools (jq, grep, etc.)
- Imported partially or completely

## Testing

### Unit Tests

Run the test suite:

```bash
pytest test_migration.py -v
```

### Round-Trip Validation

Test the complete export/import workflow:

```bash
# 1. Export current data products
python export.py --clear --entities data_products

# 2. Verify export succeeded
cat exports/export_summary.json

# 3. Test import functionality (creates new entities)
# Note: Import creates new entities, so use carefully in production
python import.py --input-dir exports --entity-type data_products --dry-run

# 4. Validate in OpenMetadata UI
# Check that exported entities maintain all relationships and metadata
```

## Troubleshooting

### Authentication Issues
- Verify your JWT token is valid and not expired
- Check server URL is correct and accessible
- Ensure you have proper permissions for the entities you're trying to export/import

### Export Issues
- Check OpenMetadata server connectivity
- Verify entity types are supported in your OpenMetadata version
- Review export logs for specific entity errors

### Import Issues
- Ensure NDJSON files are properly formatted
- Check import order for dependency issues
- Use `--dry-run` to preview imports before execution

### Performance
- Adjust `batch_size` in configuration for large datasets
- Use selective export for large instances
- Monitor memory usage with `memory_limit_mb` setting

## Development Commands (Makefile)

The project includes a Makefile with useful development commands:

```bash
# Setup and cleanup
make setup          # Run setup.sh to create virtual environment
make clean          # Clean up virtual environment and exports
make clean-exports  # Clean only export files

# Testing
make test           # Run all tests with pytest
make test-verbose   # Run tests with verbose output

# Export shortcuts
make export         # Export all entities
make export-clean   # Clean exports then export all
make export-core    # Export core entities (domains, data_products, teams)

# Import shortcuts  
make import         # Import all entities
make import-dry     # Dry run import (preview only)

# Development
make lint           # Run code linting (if configured)
make format         # Format code (if configured)
make help           # Show all available commands
```

**Usage Examples:**
```bash
# Quick setup and test
make setup
make export-core

# Clean slate export
make clean-exports
make export

# Safe import testing
make import-dry
```

## Configuration Reference

### Complete config.yaml Structure

```yaml
openmetadata:
  server_url: "http://your-openmetadata-server:8585/api"
  auth:
    jwt_token: "your_jwt_token_here"

export:
  output_dir: "./exports"
  selective:
    domains: []
    linked_data_products_only: false
    linked_assets_only: false
  entities:
    domains: true
    data_products: true
    teams: true
    # ... all other entity types
  include_deleted: false
  batch_size: 100

import:
  input_dir: "./exports"
  update_existing: true
  skip_on_error: true
  create_missing_dependencies: true
  import_order:
    - teams
    - users
    - domains
    - data_products
    # ... ordered list for dependency handling

logging:
  level: "INFO"
  console_output: true

advanced:
  request_timeout: 30
  max_retries: 3
  max_workers: 5
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Third-Party Licenses

This project uses the following open-source packages:
- **OpenMetadata SDK**: Apache 2.0 License
- **Rich**: MIT License  
- **PyYAML**: MIT License
- **Click**: BSD License
- **python-dotenv**: BSD License

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## Support

For issues and questions:
- Check the troubleshooting section above
- Review OpenMetadata documentation
- Open an issue in this repository