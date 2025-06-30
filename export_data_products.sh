#!/bin/bash
# Export all data products with domain linkage using export.py
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

python3 export.py -e data_products "$@"
