#!/bin/bash

# SWAG Pricing Intelligence Tool - React + FastAPI Launcher
# Launches both backend and frontend servers

echo "======================================="
echo "  SWAG PRICING INTELLIGENCE TOOL"
echo "  Phase 5: React + FastAPI Migration"
echo "======================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo -e "${BLUE}📦 Starting Backend (FastAPI)...${NC}"
cd "$SCRIPT_DIR/backend"
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo -e "${GREEN}✅ Backend running on http://localhost:8000 (PID: $BACKEND_PID)${NC}"
echo ""

# Wait a moment for backend to start
sleep 2

echo -e "${BLUE}⚛️  Starting Frontend (React + Vite)...${NC}"
cd "$SCRIPT_DIR/frontend"
npm run dev &
FRONTEND_PID=$!
echo -e "${GREEN}✅ Frontend starting on http://localhost:5173 (PID: $FRONTEND_PID)${NC}"
echo ""

echo -e "${YELLOW}========================================${NC}"
echo -e "${GREEN}🚀 SWAG Pricing Intelligence Tool Running!${NC}"
echo -e "${YELLOW}========================================${NC}"
echo ""
echo -e "Frontend: ${BLUE}http://localhost:5173${NC}"
echo -e "Backend:  ${BLUE}http://localhost:8000${NC}"
echo -e "API Docs: ${BLUE}http://localhost:8000/docs${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all servers${NC}"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down servers...${NC}"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo -e "${GREEN}✅ All servers stopped${NC}"
    exit 0
}

# Trap Ctrl+C and cleanup
trap cleanup INT TERM

# Wait for processes
wait
