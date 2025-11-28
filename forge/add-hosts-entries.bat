@echo off
REM ==============================================================================
REM ADD LOCAL DOMAIN ENTRIES TO HOSTS FILE
REM ==============================================================================
REM IMPORTANT: Run as Administrator (Right-click > Run as Administrator)
REM ==============================================================================

echo ==============================================================================
echo Adding local domain entries to hosts file
echo ==============================================================================
echo.

REM Check for admin rights
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script must be run as Administrator!
    echo.
    echo Right-click this file and select "Run as Administrator"
    echo.
    pause
    exit /b 1
)

set HOSTS_FILE=C:\Windows\System32\drivers\etc\hosts

REM Backup hosts file
set BACKUP_FILE=%HOSTS_FILE%.backup-%date:~-4,4%%date:~-10,2%%date:~-7,2%-%time:~0,2%%time:~3,2%%time:~6,2%
set BACKUP_FILE=%BACKUP_FILE: =0%
copy "%HOSTS_FILE%" "%BACKUP_FILE%" >nul
echo [OK] Backup created: %BACKUP_FILE%
echo.

REM Add entries
echo Adding domain entries...
echo.

echo # EPCB Workspace - Local Development >> "%HOSTS_FILE%"
echo 127.0.0.1    nexus.axoiq.com >> "%HOSTS_FILE%"
echo 127.0.0.1    api-nexus.axoiq.com >> "%HOSTS_FILE%"
echo 127.0.0.1    synapse.axoiq.com >> "%HOSTS_FILE%"
echo 127.0.0.1    api.axoiq.com >> "%HOSTS_FILE%"
echo 127.0.0.1    portal.axoiq.com >> "%HOSTS_FILE%"
echo 127.0.0.1    grafana.axoiq.com >> "%HOSTS_FILE%"
echo 127.0.0.1    loki.axoiq.com >> "%HOSTS_FILE%"
echo 127.0.0.1    pgadmin.axoiq.com >> "%HOSTS_FILE%"
echo 127.0.0.1    prisma.axoiq.com >> "%HOSTS_FILE%"

echo ==============================================================================
echo [OK] Local domain entries added successfully!
echo ==============================================================================
echo.
echo You can now access:
echo   - Nexus:    https://nexus.axoiq.com
echo   - Synapse:  https://synapse.axoiq.com
echo   - Portal:   https://portal.axoiq.com
echo   - Grafana:  https://grafana.axoiq.com
echo   - pgAdmin:  https://pgadmin.axoiq.com
echo.
echo Next step: Restart Traefik
echo   docker restart workspace-traefik
echo.
pause
