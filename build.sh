#!/usr/bin/env bash
# =============================================================================
# build.sh — Collaborative Research Datasets and Curators
# IT 566: Computer Scripting Techniques, Summer 2026
# Author: Leonardo Andres Sandino Acosta
#
# Usage:
#   bash build.sh init    — Initialize database and create tables
#   bash build.sh test    — Run unit tests with pytest
#   bash build.sh run     — Start the application
#   bash build.sh all     — init + test + run
# =============================================================================

set -e  # Exit on any error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="$SCRIPT_DIR/src"
CONFIG_FILE="$SCRIPT_DIR/config/datasets_curators_config.json"
LOGS_DIR="$SCRIPT_DIR/logs"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_header() {
    echo ""
    echo -e "${GREEN}================================================${NC}"
    echo -e "${GREEN}  Collaborative Research Datasets & Curators    ${NC}"
    echo -e "${GREEN}  IT 566 Final Project - Build Script            ${NC}"
    echo -e "${GREEN}================================================${NC}"
    echo ""
}

create_logs_dir() {
    if [ ! -d "$LOGS_DIR" ]; then
        mkdir -p "$LOGS_DIR"
        echo -e "${YELLOW}[INFO] Created logs directory: $LOGS_DIR${NC}"
    fi
}

init_database() {
    echo -e "${YELLOW}[INIT] Initializing database...${NC}"
    cd "$SRC_DIR"
    pipenv run python -c "
import sys
sys.path.insert(0, '.')
import json
from datasets_and_curators.persistence_layer.mysql_persistence_wrapper import MySQLPersistenceWrapper
with open('../config/datasets_curators_config.json', 'r') as f:
    config = json.load(f)
db = MySQLPersistenceWrapper(config)
db.initialize_database()
print('[INIT] Database initialization complete.')
"
    echo -e "${GREEN}[INIT] Done.${NC}"
}

run_tests() {
    echo -e "${YELLOW}[TEST] Running unit tests...${NC}"
    cd "$SCRIPT_DIR"
    pipenv run pytest tests/ -v
    echo -e "${GREEN}[TEST] All tests passed.${NC}"
}

run_app() {
    echo -e "${YELLOW}[RUN] Starting application...${NC}"
    cd "$SRC_DIR"
    pipenv run python main.py -c "../config/datasets_curators_config.json"
}

# ---- Main ----
print_header
create_logs_dir

case "$1" in
    init)
        init_database
        ;;
    test)
        run_tests
        ;;
    run)
        run_app
        ;;
    all)
        init_database
        run_tests
        run_app
        ;;
    *)
        echo "Usage: bash build.sh {init|test|run|all}"
        echo ""
        echo "  init  — Initialize database and create tables"
        echo "  test  — Run unit tests"
        echo "  run   — Start the application"
        echo "  all   — Run all of the above in sequence"
        exit 1
        ;;
esac
