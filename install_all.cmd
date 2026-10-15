@echo off
title All Stacks - Dependency Installer

echo ====================================================================
echo   ALL STACKS - DEPENDENCY INSTALLER
echo   Checking and installing all required Python packages...
echo ====================================================================
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    pause
    exit /b 1
)

echo [1/6] Installing Kafka dependencies...
pip install kafka-python-ng flask colorama requests jinja2 >nul 2>&1
echo       Kafka dependencies ready.

echo [2/6] Installing Keycloak dependencies...
pip install python-keycloak flask-session cryptography python-dotenv >nul 2>&1
echo       Keycloak dependencies ready.

echo [3/6] Installing IDP dependencies...
pip install PyJWT cryptography flask-cors >nul 2>&1
echo       IDP dependencies ready.

echo [4/6] Installing RAG dependencies...
pip install chromadb sentence-transformers pypdf2 transformers torch >nul 2>&1
echo       RAG dependencies ready.

echo [5/6] Installing AI Agents dependencies...
pip install jinja2 requests >nul 2>&1
echo       AI Agents dependencies ready.

echo [6/6] Initializing databases and encryption keys...
python "%~dp002-Keycloak\init_db.py" >nul 2>&1
if not exist "%~dp003-IDP\private_key.pem" (
    python "%~dp003-IDP\generate_keys.py" >nul 2>&1
)
echo       Databases and keys ready.

echo.
echo ====================================================================
echo   INSTALLATION COMPLETE!
echo   Run "run.cmd" to start all 5 projects.
echo ====================================================================
echo.
pause