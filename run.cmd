@echo off
setlocal EnableDelayedExpansion
title All Stacks - Master Runner

set "ROOT=%~dp0"
cd /d "%ROOT%"

echo ====================================================================
echo   ALL STACKS - MASTER ONE-CLICK RUNNER
echo   Launching all 5 projects simultaneously...
echo ====================================================================
echo.
echo   PORT    PROJECT                        URL
echo   ------------------------------------------------------------------
echo   5001    01-Kafka Task Queue UI         http://localhost:5001
echo   5002    02-Keycloak Secure Notes       http://localhost:5002
echo   8088    02-Keycloak Auth and Admin     http://localhost:8088
echo   5005    03-IDP Client Application      http://localhost:5005
echo   5003    03-IDP Identity Provider       http://localhost:5003
echo   5004    03-IDP Resource Server         http://localhost:5004
echo   5006    04-RAG Document QA System      http://localhost:5006
echo   5007    05-AI-Agents Multi-Agent UI    http://localhost:5007
echo   ------------------------------------------------------------------
echo.

echo [1/6] Starting 01-Kafka Consumer Worker...
start "01-Kafka Consumer" /d "%ROOT%01-Kafka" cmd /k python consumer.py
ping 127.0.0.1 -n 2 >nul

echo [2/6] Starting 01-Kafka Producer (Port 5001)...
start "01-Kafka Producer" /d "%ROOT%01-Kafka" cmd /k python producer.py
ping 127.0.0.1 -n 2 >nul

echo [3/6] Starting 02-Keycloak Notes and Auth (Port 5002 and 8088)...
start "02-Keycloak Notes" /d "%ROOT%02-Keycloak" cmd /k python app.py
ping 127.0.0.1 -n 2 >nul

echo [4/6] Starting 03-IDP Ecosystem (Ports 5003, 5004, 5005)...
start "03-IDP Ecosystem" /d "%ROOT%03-IDP" cmd /k python run_all.py
ping 127.0.0.1 -n 2 >nul

echo [5/6] Starting 04-RAG Document QA (Port 5006)...
start "04-RAG System" /d "%ROOT%04-RAG" cmd /k python app.py
ping 127.0.0.1 -n 2 >nul

echo [6/6] Starting 05-AI-Agents Multi-Agent System (Port 5007)...
start "05-AI-Agents" /d "%ROOT%05-AI-Agents" cmd /k python run.py
ping 127.0.0.1 -n 3 >nul

echo.
echo ====================================================================
echo   ALL 5 PROJECTS ARE NOW RUNNING!
echo.
echo   01-Kafka:     http://localhost:5001
echo   02-Keycloak:  http://localhost:5002  (Auth: http://localhost:8088)
echo   03-IDP:       http://localhost:5005
echo   04-RAG:       http://localhost:5006
echo   05-AI-Agents: http://localhost:5007
echo.
echo   To check ports: run check_status.cmd
echo   To stop all:    run stop.cmd
echo ====================================================================
echo.

echo Opening dashboards in default web browser...
ping 127.0.0.1 -n 3 >nul
start "" "http://localhost:5001"
start "" "http://localhost:5002"
start "" "http://localhost:5005"
start "" "http://localhost:5006"
start "" "http://localhost:5007"

echo Done. All windows are open.