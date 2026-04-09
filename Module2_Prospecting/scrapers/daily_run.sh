#!/bin/bash

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
VENV_PYTHON="$PROJECT_ROOT/.venv/bin/python"

echo "==================================="
echo "BMW iX Daily Prospecting Run"
echo "Date: $(date)"
echo "==================================="
echo ""

echo "[1/2] Running BMW CPO Playwright Scraper..."
cd "$PROJECT_ROOT" || exit
"$VENV_PYTHON" "$SCRIPT_DIR/bmw_cpo_scraper.py"

if [ $? -ne 0 ]; then
    echo "Scraper failed. Exiting."
    exit 1
fi

echo ""
echo "[2/2] Running Inventory Database Upsert..."
"$VENV_PYTHON" "$SCRIPT_DIR/update_inventory.py"

if [ $? -ne 0 ]; then
    echo "Inventory updater failed. Exiting."
    exit 1
fi

echo ""
echo "[3/3] Generating Markdown Value Matrix Report..."
"$VENV_PYTHON" "$SCRIPT_DIR/../reports/generate_report.py"

if [ $? -ne 0 ]; then
    echo "Report generator failed. Exiting."
    exit 1
fi

echo ""
echo "==================================="
echo "Daily Run Completely Successfully!"
echo "==================================="
