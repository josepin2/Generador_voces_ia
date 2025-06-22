@echo off
echo Instalando el Generador de Voces...
echo.

rem Crear entorno virtual si no existe
if not exist venv (
    echo Creando entorno virtual...
    python -m venv venv
)

rem Activar entorno virtual
call venv\Scripts\activate

rem Instalar dependencias
echo Instalando dependencias...
pip install -r requirements.txt

rem Crear directorios necesarios
if not exist static\audio mkdir static\audio
if not exist sonidos mkdir sonidos

echo.
echo Instalacion completada!
echo.
echo Para ejecutar la aplicacion:
echo 1. Asegurate de que FFmpeg este instalado
echo 2. Coloca archivos MP3 en la carpeta 'sonidos' si quieres musica de fondo
echo 3. Ejecuta 'python app.py'
echo.
pause
