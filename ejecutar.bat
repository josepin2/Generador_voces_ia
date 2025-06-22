@echo off
echo Iniciando el generador de voces...

:: Activar el entorno virtual
call venv\Scripts\activate.bat

:: Iniciar la aplicación Flask en segundo plano
start /B python app.py

:: Esperar 2 segundos para que Flask inicie
timeout /t 2 /nobreak > nul

:: Abrir el navegador
start http://127.0.0.1:5000

echo La aplicación está lista. Presiona Ctrl+C en la ventana de la consola para detener el servidor.
echo.

:: Mantener la ventana abierta
pause 