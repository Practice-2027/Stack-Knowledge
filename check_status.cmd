@echo off
title All Stacks - Health Check

echo.
echo ====================================================================
echo   ALL STACKS - PORT AND SERVICE STATUS
echo ====================================================================
echo.
echo   PORT    SERVICE                         STATUS
echo   -------------------------------------------------

netstat -an | findstr ":5001 " | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo   5001    01-Kafka Task Queue UI          ONLINE
) else (
    echo   5001    01-Kafka Task Queue UI          OFFLINE
)

netstat -an | findstr ":5002 " | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo   5002    02-Keycloak Secure Notes        ONLINE
) else (
    echo   5002    02-Keycloak Secure Notes        OFFLINE
)

netstat -an | findstr ":8088 " | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo   8088    02-Keycloak Auth and Admin      ONLINE
) else (
    echo   8088    02-Keycloak Auth and Admin      OFFLINE
)

netstat -an | findstr ":5003 " | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo   5003    03-IDP Identity Provider        ONLINE
) else (
    echo   5003    03-IDP Identity Provider        OFFLINE
)

netstat -an | findstr ":5004 " | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo   5004    03-IDP Resource Server          ONLINE
) else (
    echo   5004    03-IDP Resource Server          OFFLINE
)

netstat -an | findstr ":5005 " | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo   5005    03-IDP Client Web App           ONLINE
) else (
    echo   5005    03-IDP Client Web App           OFFLINE
)

netstat -an | findstr ":5006 " | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo   5006    04-RAG Document QA System       ONLINE
) else (
    echo   5006    04-RAG Document QA System       OFFLINE
)

netstat -an | findstr ":5007 " | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo   5007    05-AI-Agents Multi-Agent UI     ONLINE
) else (
    echo   5007    05-AI-Agents Multi-Agent UI     OFFLINE
)

echo   -------------------------------------------------
echo.
echo Web Dashboards:
echo   http://localhost:5001  (01-Kafka)
echo   http://localhost:5002  (02-Keycloak Notes)
echo   http://localhost:8088  (02-Keycloak Auth)
echo   http://localhost:5005  (03-IDP Client)
echo   http://localhost:5006  (04-RAG Document QA)
echo   http://localhost:5007  (05-AI-Agents)
echo.
pause