@echo off
REM Script rápido para ejecutar SuperMercado (versión compilada)

cd /d "%~dp0"

echo.
echo ====================================
echo SuperMercado - Iniciando...
echo ====================================
echo.

REM Iniciar servidor Java
echo Iniciando servidor Java en puerto 5000...
start "SuperMercado-Server" /min java -jar ..\Java\target\conexion-server-1.0-jar-with-dependencies.jar

REM Esperar a que el servidor esté listo
echo Esperando que el servidor inicie (3 segundos)...
timeout /t 3 /nobreak

REM Iniciar interfaz
echo Iniciando interfaz grafica...
cd ..\app\python
python ui_principal.py
cd ..\scripts

REM Limpiar
echo Cerrando servidor...
taskkill /FI "WINDOWTITLE eq SuperMercado-Server" /F >nul 2>&1
echo SuperMercado finalizado.
