#!/bin/bash

# Test Domain Import Script for OMD Migration
# This script imports a single domain (and its subdomains) into your target OMD instance for testing

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== OMD Domain Import Test ===${NC}"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${RED}Error: .env file not found${NC}"
    echo "Please create .env file with your OMD configuration"
    exit 1
fi

# Convert .env to Unix line endings if needed
if file .env | grep -q "CRLF"; then
    echo -e "${YELLOW}Converting .env from Windows to Unix line endings...${NC}"
    dos2unix .env 2>/dev/null || sed -i 's/\r$//' .env
fi

# Load environment variables
set -a
source .env
set +a

# Validate required environment variables
if [ -z "$OPENMETADATA_SERVER_URL" ]; then
    echo -e "${RED}Error: OPENMETADATA_SERVER_URL not set in .env${NC}"
    exit 1
fi

if [ -z "$OPENMETADATA_JWT_TOKEN" ]; then
    echo -e "${RED}Error: OPENMETADATA_JWT_TOKEN not set in .env${NC}"
    exit 1
fi

# Find available Python command
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo -e "${RED}Error: Python not found. Please install Python in WSL.${NC}"
    echo "Install with: sudo apt update && sudo apt install python3 python3-pip"
    exit 1
fi

echo -e "${YELLOW}Using Python command: $PYTHON_CMD${NC}"

echo -e "${YELLOW}Target OMD Server: $OPENMETADATA_SERVER_URL${NC}"

# Prompt user for export subdirectory containing domains.ndjson
while true; do
    read -rp "Enter the export subdirectory containing domains.ndjson (e.g., ./exports/domain_test_YYYYMMDD_HHMMSS): " EXPORT_DIR
    DOMAIN_FILE="$EXPORT_DIR/domains.ndjson"
    if [ -f "$DOMAIN_FILE" ]; then
        break
    else
        echo -e "${RED}Error: domains.ndjson not found in $EXPORT_DIR${NC}"
        # Optionally, list available subdirectories
        echo -e "${YELLOW}Available export subdirectories:${NC}"
        find ./exports -type f -name domains.ndjson | sed 's|/domains.ndjson||' | nl
        echo
    fi
done

# Step 1: Importing ALL Domains (Dry-run)
echo -e "\n${BLUE}=== Step 1: Importing ALL Domains (Dry-run) ===${NC}"
$PYTHON_CMD import.py --input-dir "$EXPORT_DIR" --entity-type domains --dry-run || {
    echo -e "${RED}✗ All domains import dry-run failed${NC}"
    exit 1
}
echo -e "${GREEN}✓ All domains import dry-run completed successfully${NC}"

read -rp "Proceed with actual import of ALL domains? (y/n): " CONFIRM_ALL
if [[ "$CONFIRM_ALL" =~ ^[Yy]$ ]]; then
    $PYTHON_CMD import.py --input-dir "$EXPORT_DIR" --entity-type domains
    echo -e "${GREEN}✓ All domains import completed successfully${NC}"
else
    echo -e "${YELLOW}All domains import cancelled by user.${NC}"
fi

echo -e "\n${BLUE}Import script finished.${NC}"
