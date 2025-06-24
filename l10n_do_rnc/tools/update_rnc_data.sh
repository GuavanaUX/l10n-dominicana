#!/bin/bash

# Script to automate the update of RNC data
# Usage: ./update_rnc_data.sh [DOWNLOAD_URL]

set -e  # Exit if any error occurs

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODULE_DIR="$(dirname "$SCRIPT_DIR")"
DATA_DIR="$MODULE_DIR/data"
TOOLS_DIR="$MODULE_DIR/tools"
TEMP_ZIP="DGII_RNC.zip"
TEMP_FILE="DGII_RNC_TEMP.TXT"

# Default URL (can be overridden as a parameter)
DEFAULT_URL="https://www.dgii.gov.do/app/WebApps/Consultas/RNC/DGII_RNC.zip"
DOWNLOAD_URL="${1:-$DEFAULT_URL}"

echo -e "${BLUE}Starting RNC data update...${NC}"
echo -e "${YELLOW}Download URL: $DOWNLOAD_URL${NC}"

# Verify that we are in the correct directory
if [[ ! -f "$MODULE_DIR/__manifest__.py" ]]; then
    echo -e "${RED}Error: __manifest__.py file not found${NC}"
    echo -e "${YELLOW}Make sure to run this script from the module directory${NC}"
    exit 1
fi

# Create directories if they don't exist
mkdir -p "$DATA_DIR"

# Download ZIP file
echo -e "${BLUE}Descargando archivo RNC (ZIP)...${NC}"
if curl -L -o "$TEMP_ZIP" "$DOWNLOAD_URL"; then
    echo -e "${GREEN}ZIP file downloaded successfully${NC}"
else
    echo -e "${RED}Error downloading file${NC}"
    exit 1
fi

# Verify that the ZIP file was downloaded correctly
if [[ ! -f "$TEMP_ZIP" ]] || [[ ! -s "$TEMP_ZIP" ]]; then
    echo -e "${RED}Error: ZIP file is empty or not found${NC}"
    exit 1
fi

# Extract ZIP file
echo -e "${BLUE}Extracting ZIP file...${NC}"
if unzip -q "$TEMP_ZIP"; then
    echo -e "${GREEN}ZIP file extracted successfully${NC}"
else
    echo -e "${RED}Error extracting ZIP file${NC}"
    rm -f "$TEMP_ZIP"
    exit 1
fi

# Search for TXT file in TMP folder
echo -e "${BLUE}Searching for TXT file in TMP folder...${NC}"
if [[ -d "TMP" ]] && [[ -n "$(find TMP -name '*.txt' -type f)" ]]; then
    TXT_FILE=$(find TMP -name '*.txt' -type f | head -1)
    echo -e "${BLUE}Copying file: $TXT_FILE${NC}"
    cp "$TXT_FILE" "$TEMP_FILE"
else
    echo -e "${RED}Error: TXT file not found in TMP folder${NC}"
    rm -f "$TEMP_ZIP"
    rm -rf "TMP" 2>/dev/null || true
    exit 1
fi

# Verify that the TXT file was copied
if [[ ! -f "$TEMP_FILE" ]]; then
    echo -e "${RED}Error: TXT file not copied${NC}"
    rm -f "$TEMP_ZIP"
    rm -rf "TMP" 2>/dev/null || true
    exit 1
fi
echo -e "${GREEN}TXT file extracted successfully${NC}"

# Convert file
echo -e "${BLUE}Converting file to compressed JSON...${NC}"
if python3 "$TOOLS_DIR/convert_rnc_data.py" "$TEMP_FILE" "$DATA_DIR"; then
    echo -e "${GREEN}Conversion completed${NC}"
else
    echo -e "${RED}Error in conversion${NC}"
    rm -f "$TEMP_FILE"
    rm -f "$TEMP_ZIP"
    rm -rf "TMP" 2>/dev/null || true
    exit 1
fi

# Clean temporary files
rm -f "$TEMP_FILE"
rm -f "$TEMP_ZIP"
rm -rf "TMP" 2>/dev/null || true

# Show statistics of the generated file
if [[ -f "$DATA_DIR/rnc_data.json.gz" ]]; then
    FILE_SIZE=$(du -h "$DATA_DIR/rnc_data.json.gz" | cut -f1)
    echo -e "${GREEN}Generated file: $DATA_DIR/rnc_data.json.gz ($FILE_SIZE)${NC}"
    echo -e "${GREEN}Process completed successfully${NC}"
else
    echo -e "${RED}Error: Data file not generated${NC}"
    exit 1
fi

echo -e "${GREEN} RNC data update completed!${NC}"
echo -e "${YELLOW} Remember to update the module in the clients: -u l10n_do_rnc${NC}"