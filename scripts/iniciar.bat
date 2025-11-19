@echo off
cd /d "%~dp0"
echo.
echo ====================================
echo SuperMercado - Iniciando...
echo ====================================
echo.
echo Iniciando servidor Java en puerto 5000...
start "SuperMercado-Server" /min java -jar ..\Java\target\conexion-server-1.0-jar-with-dependencies.jar
echo Esperando que el servidor inicie (3 segundos)...
timeout /t 3 /nobreak
echo Iniciando interfaz grafica...
cd ..\app\python
python ui_principal.py
cd ..\scripts
echo Cerrando servidor...
taskkill /FI "WINDOWTITLE eq SuperMercado-Server" /F >nul 2>&1
echo SuperMercado finalizado.
