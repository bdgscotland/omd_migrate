#!/bin/bash

# Test Domain Export Script for OMD Migration
# This script exports domains from your source OMD instance for testing

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== OMD Domain Export Test ===${NC}"

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

echo -e "${YELLOW}Source OMD Server: $OPENMETADATA_SERVER_URL${NC}"
echo -e "${YELLOW}Export Directory: ${EXPORT_OUTPUT_DIR:-./exports}${NC}"

# Create export directory if it doesn't exist
EXPORT_DIR="${EXPORT_OUTPUT_DIR:-./exports}"
mkdir -p "$EXPORT_DIR"

# Create a test-specific subdirectory with timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
TEST_EXPORT_DIR="$EXPORT_DIR/domain_test_$TIMESTAMP"
mkdir -p "$TEST_EXPORT_DIR"

echo -e "${BLUE}Test export directory: $TEST_EXPORT_DIR${NC}"

# Test 1: Export only domains
echo -e "\n${BLUE}=== Test 1: Exporting Domains ===${NC}"
$PYTHON_CMD export.py \
    --entities domains \
    --output-dir "$TEST_EXPORT_DIR" \
    $([ "${EXPORT_INCLUDE_DELETED:-false}" = "true" ] && echo "--include-deleted")

# Check if export was successful
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Domain export completed successfully${NC}"
else
    echo -e "${RED}✗ Domain export failed${NC}"
    exit 1
fi

# Test 2: Validate exported files
echo -e "\n${BLUE}=== Test 2: Validating Export Files ===${NC}"

DOMAIN_FILE="$TEST_EXPORT_DIR/domains.ndjson"
if [ -f "$DOMAIN_FILE" ]; then
    DOMAIN_COUNT=$(wc -l < "$DOMAIN_FILE")
    echo -e "${GREEN}✓ Found domain export file with $DOMAIN_COUNT domains${NC}"
    
    # Show first few domains (preview)
    echo -e "\n${YELLOW}Preview of exported domains:${NC}"
    head -3 "$DOMAIN_FILE" | jq -r '.name // .displayName // "Unknown"' 2>/dev/null || head -3 "$DOMAIN_FILE"
    
    if [ $DOMAIN_COUNT -gt 3 ]; then
        echo "... and $(($DOMAIN_COUNT - 3)) more domains"
    fi
else
    echo -e "${RED}✗ No domain export file found${NC}"
    exit 1
fi

# Test 3: Validate JSON structure
echo -e "\n${BLUE}=== Test 3: Validating JSON Structure ===${NC}"
if command -v jq &> /dev/null; then
    if jq empty "$DOMAIN_FILE" 2>/dev/null; then
        echo -e "${GREEN}✓ All exported domains have valid JSON structure${NC}"
    else
        echo -e "${RED}✗ Invalid JSON detected in export file${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠ jq not installed, skipping JSON validation${NC}"
fi

# Test 4: Generate export summary
echo -e "\n${BLUE}=== Test 4: Export Summary ===${NC}"

# Create summary file
SUMMARY_FILE="$TEST_EXPORT_DIR/export_summary.txt"
cat > "$SUMMARY_FILE" << EOF
OMD Domain Export Summary
========================
Export Date: $(date)
Source Server: $OPENMETADATA_SERVER_URL
Export Directory: $TEST_EXPORT_DIR

Files Created:
EOF

# List all created files with sizes
for file in "$TEST_EXPORT_DIR"/*.ndjson; do
    if [ -f "$file" ]; then
        FILENAME=$(basename "$file")
        SIZE=$(wc -l < "$file")
        echo "  $FILENAME: $SIZE records" >> "$SUMMARY_FILE"
        echo -e "${GREEN}  $FILENAME: $SIZE records${NC}"
    fi
done

echo -e "\n${YELLOW}Export summary saved to: $SUMMARY_FILE${NC}"

# Test 5: Quick import validation (dry-run)
echo -e "\n${BLUE}=== Test 5: Import Validation (Dry-run) ===${NC}"
echo "To test import to target instance:"
echo "1. Update .env with target OMD server details"
echo "2. Run: $PYTHON_CMD import.py --input-dir \"$TEST_EXPORT_DIR\" --dry-run"

echo -e "\n${GREEN}=== Domain Export Test Completed Successfully ===${NC}"
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Review exported files in: $TEST_EXPORT_DIR"
echo "2. Configure target OMD instance in .env"
echo "3. Test import with --dry-run flag first"
echo "4. Perform actual import when ready"

echo -e "\n${BLUE}Export location: $TEST_EXPORT_DIR${NC}"
