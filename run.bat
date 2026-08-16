@echo off
echo ============================================
echo  Urban Environmental Hazard AI - Quick Start
echo ============================================

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate

echo Installing PyTorch (CPU build)...
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

echo Installing backend dependencies...
pip install -r requirements.txt

echo Starting backend on http://localhost:8000 ...
start "Backend" cmd /k "call venv\Scripts\activate && cd backend && python app.py"

echo Installing frontend dependencies (first run only)...
cd frontend
if not exist node_modules (
    call npm install
)

echo Starting frontend on http://localhost:5173 ...
start "Frontend" cmd /k "npm run dev"

cd ..
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo.
pause
