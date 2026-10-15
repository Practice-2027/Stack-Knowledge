@echo off
title All Stacks - Stop All Projects

echo.
echo ====================================================================
echo   ALL STACKS - STOP ALL PROJECTS
echo ====================================================================
echo.

echo Stopping Python server windows...
taskkill /FI "WINDOWTITLE eq 01-Kafka*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq 02-Keycloak*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq 03-IDP*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq 04-RAG*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq 05-AI-Agents*" /F >nul 2>&1

echo Stopping Docker containers (if running)...
docker compose -f "%~dp001-Kafka\docker-compose.yml" down >nul 2>&1
docker compose -f "%~dp002-Keycloak\docker-compose.yml" down >nul 2>&1

echo.
echo ====================================================================
echo   ALL PROJECTS HAVE BEEN STOPPED!
echo   Ports 5001-5007 and 8088 are now released.
echo ====================================================================
echo.
pause