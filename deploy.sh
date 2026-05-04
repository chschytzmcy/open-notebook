#!/bin/bash
set -e

# ============================================
# Open Notebook Deploy Script
# ============================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Arguments
SKIP_BUILD=false
BUILD_ONLY=false
for arg in "$@"; do
    case $arg in
        --no-build|-n)
            SKIP_BUILD=true
            ;;
        --build-only|-b)
            BUILD_ONLY=true
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --build-only, -b   Only build images, don't start services"
            echo "  --no-build, -n     Deploy without building (use existing images)"
            echo "  --help, -h         Show this help message"
            exit 0
            ;;
    esac
done

# Check if .env exists
if [ ! -f ".env" ]; then
    log_warn ".env file not found, copying from .env.example..."
    cp .env.example .env
fi

# Check for encryption key
if grep -q "change-me-to-a-secret-string" .env 2>/dev/null; then
    log_warn "OPEN_NOTEBOOK_ENCRYPTION_KEY is still set to default value!"
    log_warn "Please edit .env and set a secure encryption key before deploying."
fi

# Stop existing containers
log_info "Stopping existing containers..."
docker compose down 2>/dev/null || true

# Build images
if [ "$SKIP_BUILD" = true ]; then
    log_info "Skipping build (using existing images)..."
else
    log_info "Building Docker image..."
    docker compose build --pull
fi

# Start services
if [ "$BUILD_ONLY" = true ]; then
    log_info "Build complete, services not started (--build-only)"
    exit 0
fi

log_info "Starting services..."
docker compose up -d

# Wait for services to be ready
log_info "Waiting for services to start..."
sleep 5

# Check status
log_info "Checking service status..."
docker compose ps

# Show URLs
echo ""
log_info "Open Notebook deployed successfully!"
log_info "  Web UI:    http://localhost:8502"
log_info "  REST API:  http://localhost:5055"
log_info "  API Docs:  http://localhost:5055/docs"