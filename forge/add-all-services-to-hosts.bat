@echo off
REM ==============================================================================
REM ADD ALL WORKSPACE SERVICES TO HOSTS FILE
REM ==============================================================================
REM Run as Administrator
REM ==============================================================================

echo ==============================================================================
echo Adding ALL workspace services to hosts file
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

echo Adding workspace service entries...
echo.

REM Remove existing EPCB Workspace entries if any
findstr /v "EPCB Workspace" "%HOSTS_FILE%" > "%HOSTS_FILE%.tmp"
move /y "%HOSTS_FILE%.tmp" "%HOSTS_FILE%" >nul 2>&1

REM Add all service entries
echo # ============================================================================== >> "%HOSTS_FILE%"
echo # EPCB Workspace - Local Development (axoiq.com) >> "%HOSTS_FILE%"
echo # ============================================================================== >> "%HOSTS_FILE%"
echo.
echo # Nexus - Knowledge Graph Portal >> "%HOSTS_FILE%"
echo 127.0.0.1    nexus.axoiq.com >> "%HOSTS_FILE%"
echo 127.0.0.1    api-nexus.axoiq.com >> "%HOSTS_FILE%"
echo.
echo # Synapse - Task Management >> "%HOSTS_FILE%"
echo 127.0.0.1    synapse.axoiq.com >> "%HOSTS_FILE%"
echo 127.0.0.1    api.axoiq.com >> "%HOSTS_FILE%"
echo.
echo # Homepage Portal >> "%HOSTS_FILE%"
echo 127.0.0.1    portal.axoiq.com >> "%HOSTS_FILE%"
echo.
echo # Owner Portal >> "%HOSTS_FILE%"
echo 127.0.0.1    owner.axoiq.com >> "%HOSTS_FILE%"
echo.
echo # Monitoring & Observability >> "%HOSTS_FILE%"
echo 127.0.0.1    grafana.axoiq.com >> "%HOSTS_FILE%"
echo 127.0.0.1    loki.axoiq.com >> "%HOSTS_FILE%"
echo.
echo # Database Management >> "%HOSTS_FILE%"
echo 127.0.0.1    pgadmin.axoiq.com >> "%HOSTS_FILE%"
echo 127.0.0.1    prisma.axoiq.com >> "%HOSTS_FILE%"
echo.
echo # Testing & Quality >> "%HOSTS_FILE%"
echo 127.0.0.1    reportportal.axoiq.com >> "%HOSTS_FILE%"
echo 127.0.0.1    allure.axoiq.com >> "%HOSTS_FILE%"
echo.
echo # Infrastructure >> "%HOSTS_FILE%"
echo 127.0.0.1    portainer.axoiq.com >> "%HOSTS_FILE%"
echo 127.0.0.1    traefik.axoiq.com >> "%HOSTS_FILE%"
echo # ============================================================================== >> "%HOSTS_FILE%"

echo ==============================================================================
echo [OK] All workspace services added to hosts file!
echo ==============================================================================
echo.
echo You can now access via HTTPS (with valid SSL):
echo.
echo   APPLICATIONS:
echo   - Nexus:          https://nexus.axoiq.com
echo   - Synapse:        https://synapse.axoiq.com
echo   - Homepage:       https://portal.axoiq.com
echo   - Owner Portal:   https://owner.axoiq.com
echo.
echo   MONITORING:
echo   - Grafana:        https://grafana.axoiq.com
echo   - Loki:           https://loki.axoiq.com
echo.
echo   DATABASE:
echo   - pgAdmin:        https://pgadmin.axoiq.com
echo   - Prisma Studio:  https://prisma.axoiq.com
echo.
echo   TESTING:
echo   - ReportPortal:   https://reportportal.axoiq.com
echo   - Allure:         https://allure.axoiq.com
echo.
echo   INFRASTRUCTURE:
echo   - Portainer:      https://portainer.axoiq.com
echo   - Traefik:        https://traefik.axoiq.com
echo.
echo Next step: Restart Traefik to load all routes
echo   docker restart workspace-traefik
echo.
pause
