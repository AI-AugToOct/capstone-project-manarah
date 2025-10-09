#!/bin/bash

# Manarah Setup Verification Script
# This script verifies your Docker and Railway setup is correct

echo "🔍 Manarah Setup Verification"
echo "=============================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0
WARNINGS=0

# Helper functions
pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASSED++))
}

fail() {
    echo -e "${RED}✗${NC} $1"
    ((FAILED++))
}

warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((WARNINGS++))
}

# Check Docker
echo "📦 Checking Docker..."
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
    pass "Docker installed (v$DOCKER_VERSION)"
else
    fail "Docker not installed"
fi

if command -v docker compose &> /dev/null; then
    COMPOSE_VERSION=$(docker compose version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
    pass "Docker Compose installed (v$COMPOSE_VERSION)"
else
    fail "Docker Compose not installed"
fi

# Check if Docker daemon is running
if docker info &> /dev/null; then
    pass "Docker daemon is running"
else
    fail "Docker daemon is not running"
fi

echo ""

# Check project structure
echo "📁 Checking project structure..."
if [ -d "capstone-project-manarah" ]; then
    pass "Frontend directory exists"
else
    fail "Frontend directory not found"
fi

if [ -d "capstone-project-manarah-backend" ]; then
    pass "Backend directory exists"
else
    fail "Backend directory not found"
fi

echo ""

# Check Dockerfiles
echo "🐳 Checking Dockerfiles..."
if [ -f "capstone-project-manarah/Dockerfile" ]; then
    pass "Frontend Dockerfile exists"
else
    fail "Frontend Dockerfile not found"
fi

if [ -f "capstone-project-manarah-backend/Dockerfile" ]; then
    pass "Backend Dockerfile exists"
else
    fail "Backend Dockerfile not found"
fi

echo ""

# Check Docker Compose files
echo "📝 Checking Compose files..."
if [ -f "docker-compose.dev.yml" ]; then
    pass "Dev compose file exists"
else
    fail "docker-compose.dev.yml not found"
fi

if [ -f "docker-compose.yml" ]; then
    pass "Prod compose file exists"
else
    fail "docker-compose.yml not found"
fi

echo ""

# Check .env files
echo "🔐 Checking environment files..."
if [ -f "capstone-project-manarah-backend/.env" ]; then
    pass "Backend .env exists"

    # Check for OpenAI key
    if grep -q "OPENAI_API_KEY=sk-" "capstone-project-manarah-backend/.env"; then
        pass "OpenAI API key appears to be set"
    else
        warn "OpenAI API key not set or invalid format"
    fi
else
    fail "Backend .env not found (copy from .env.example)"
fi

if [ -f "capstone-project-manarah/.env.example" ]; then
    pass "Frontend .env.example exists"
else
    warn "Frontend .env.example not found"
fi

echo ""

# Check .dockerignore files
echo "🚫 Checking .dockerignore files..."
if [ -f ".dockerignore" ]; then
    pass "Root .dockerignore exists"
else
    warn "Root .dockerignore not found"
fi

if [ -f "capstone-project-manarah/.dockerignore" ]; then
    pass "Frontend .dockerignore exists"
else
    warn "Frontend .dockerignore not found"
fi

if [ -f "capstone-project-manarah-backend/.dockerignore" ]; then
    pass "Backend .dockerignore exists"
else
    warn "Backend .dockerignore not found"
fi

echo ""

# Check dependencies
echo "📚 Checking dependency files..."
if [ -f "capstone-project-manarah/package.json" ]; then
    pass "Frontend package.json exists"
else
    fail "Frontend package.json not found"
fi

if [ -f "capstone-project-manarah-backend/requirements.txt" ]; then
    pass "Backend requirements.txt exists"
else
    fail "Backend requirements.txt not found"
fi

echo ""

# Check documentation
echo "📖 Checking documentation..."
if [ -f "README.md" ]; then
    pass "README.md exists"
else
    warn "README.md not found"
fi

if [ -f "DOCKER_SETUP.md" ]; then
    pass "DOCKER_SETUP.md exists"
else
    warn "DOCKER_SETUP.md not found"
fi

if [ -f "RAILWAY_DEPLOY.md" ]; then
    pass "RAILWAY_DEPLOY.md exists"
else
    warn "RAILWAY_DEPLOY.md not found"
fi

if [ -f "railway.toml" ]; then
    pass "railway.toml exists"
else
    warn "railway.toml not found"
fi

echo ""

# Check Railway CLI (optional)
echo "🚂 Checking Railway CLI (optional)..."
if command -v railway &> /dev/null; then
    RAILWAY_VERSION=$(railway version)
    pass "Railway CLI installed ($RAILWAY_VERSION)"
else
    warn "Railway CLI not installed (optional, install with: npm i -g @railway/cli)"
fi

echo ""

# Check ports availability
echo "🔌 Checking port availability..."
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    warn "Port 8000 is in use (backend port)"
else
    pass "Port 8000 is available"
fi

if lsof -Pi :5173 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    warn "Port 5173 is in use (frontend dev port)"
else
    pass "Port 5173 is available"
fi

if lsof -Pi :4173 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    warn "Port 4173 is in use (frontend prod port)"
else
    pass "Port 4173 is available"
fi

echo ""

# Summary
echo "=============================="
echo "📊 Summary"
echo "=============================="
echo -e "${GREEN}Passed:${NC}   $PASSED"
echo -e "${RED}Failed:${NC}   $FAILED"
echo -e "${YELLOW}Warnings:${NC} $WARNINGS"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ Setup verification complete! You're ready to start.${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Ensure OPENAI_API_KEY is set in capstone-project-manarah-backend/.env"
    echo "2. Run: docker compose -f docker-compose.dev.yml up --build"
    echo "3. Access frontend: http://localhost:5173"
    echo "4. Access backend: http://localhost:8000/docs"
    echo ""
    exit 0
else
    echo -e "${RED}✗ Setup verification failed. Please fix the issues above.${NC}"
    echo ""
    echo "Common fixes:"
    echo "- Install Docker: https://docs.docker.com/get-docker/"
    echo "- Copy .env.example to .env in backend directory"
    echo "- Add your OpenAI API key to backend/.env"
    echo ""
    exit 1
fi
