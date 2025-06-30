#!/bin/bash

# Validate Domain Export Script
# Quick validation of exported domain data

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

if [ $# -eq 0 ]; then
    echo "Usage: $0 <export_directory>"
    echo "Example: $0 ./exports/domain_test_20250630_143022"
    exit 1
fi

EXPORT_DIR="$1"

if [ ! -d "$EXPORT_DIR" ]; then
    echo -e "${RED}Error: Directory $EXPORT_DIR does not exist${NC}"
    exit 1
fi

echo -e "${BLUE}=== Validating Domain Export: $EXPORT_DIR ===${NC}"

DOMAIN_FILE="$EXPORT_DIR/domain.ndjson"

if [ ! -f "$DOMAIN_FILE" ]; then
    echo -e "${RED}Error: domain.ndjson not found in $EXPORT_DIR${NC}"
    exit 1
fi

TOTAL_DOMAINS=$(wc -l < "$DOMAIN_FILE")
echo -e "${GREEN}Total domains exported: $TOTAL_DOMAINS${NC}"

if [ $TOTAL_DOMAINS -eq 0 ]; then
    echo -e "${YELLOW}No domains found in export${NC}"
    exit 0
fi

echo -e "\n${BLUE}=== Domain Analysis ===${NC}"

# Check if jq is available for detailed analysis
if command -v jq &> /dev/null; then
    echo "Analyzing domain structure..."
    
    # Extract domain names
    echo -e "\n${YELLOW}Domain Names:${NC}"
    jq -r '.name // .displayName // "Unknown"' "$DOMAIN_FILE" | head -10
    
    if [ $TOTAL_DOMAINS -gt 10 ]; then
        echo "... and $(($TOTAL_DOMAINS - 10)) more"
    fi
    
    # Check for required fields
    echo -e "\n${YELLOW}Field Analysis:${NC}"
    
    # Count domains with descriptions
    DOMAINS_WITH_DESC=$(jq -r 'select(.description != null and .description != "") | .name' "$DOMAIN_FILE" | wc -l)
    echo -e "  Domains with descriptions: ${GREEN}$DOMAINS_WITH_DESC/$TOTAL_DOMAINS${NC}"
    
    # Count domains with owners
    DOMAINS_WITH_OWNERS=$(jq -r 'select(.owners != null and (.owners | length) > 0) | .name' "$DOMAIN_FILE" | wc -l)
    echo -e "  Domains with owners: ${GREEN}$DOMAINS_WITH_OWNERS/$TOTAL_DOMAINS${NC}"
    
    # Check domain types if present
    DOMAIN_TYPES=$(jq -r '.domainType // "Not specified"' "$DOMAIN_FILE" | sort | uniq -c)
    if [ -n "$DOMAIN_TYPES" ]; then
        echo -e "\n${YELLOW}Domain Types:${NC}"
        echo "$DOMAIN_TYPES"
    fi
    
    echo -e "\n${YELLOW}Sample Domain Structure:${NC}"
    head -1 "$DOMAIN_FILE" | jq '.' | head -20
    
else
    echo -e "${YELLOW}jq not available - showing raw preview:${NC}"
    head -3 "$DOMAIN_FILE"
fi

# File size check
FILE_SIZE=$(ls -lh "$DOMAIN_FILE" | awk '{print $5}')
echo -e "\n${BLUE}Export file size: $FILE_SIZE${NC}"

# Check for common issues
echo -e "\n${BLUE}=== Validation Checks ===${NC}"

# Check for empty lines
EMPTY_LINES=$(grep -c '^$' "$DOMAIN_FILE" || true)
if [ $EMPTY_LINES -gt 0 ]; then
    echo -e "${YELLOW}⚠ Found $EMPTY_LINES empty lines${NC}"
else
    echo -e "${GREEN}✓ No empty lines found${NC}"
fi

# Basic JSON validation
if command -v jq &> /dev/null; then
    if jq empty "$DOMAIN_FILE" 2>/dev/null; then
        echo -e "${GREEN}✓ All JSON records are valid${NC}"
    else
        echo -e "${RED}✗ Invalid JSON found${NC}"
        echo "Checking for problematic lines..."
        jq empty "$DOMAIN_FILE" 2>&1 | head -5
    fi
fi

echo -e "\n${GREEN}=== Validation Complete ===${NC}"

# Suggest next steps
echo -e "\n${YELLOW}Next Steps:${NC}"
echo "1. Review the domain data above"
echo "2. If satisfied, prepare target OMD instance"
echo "3. Test import with: python import.py --input-dir \"$EXPORT_DIR\" --dry-run"
echo "4. Execute actual import when ready"
