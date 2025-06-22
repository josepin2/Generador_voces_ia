# Generador de Voces IA

Generador de voz a partir de texto con opción de música de fondo y generación de texto por IA local usando Ollama.

## Características
- Convierte texto a voz usando Microsoft Edge TTS.
- Permite mezclar la voz con música de fondo (archivos MP3/WAV).
- Puedes pedir a una IA local (Ollama + gemma3:4b-it-qat) que genere el texto automáticamente.
- Interfaz web moderna, tema oscuro y gestión de voces favoritas.

## Instalación

### Requisitos previos
- **Python 3.8 o superior**
- **FFmpeg** instalado y en el PATH
- **Ollama** instalado y funcionando en local ([ver guía](https://ollama.com/))
- Modelo IA local: `gemma3:4b-it-qat` (puedes instalarlo con `ollama pull gemma3:4b-it-qat`)

### Pasos
1. Clona este repositorio:
   ```sh
   git clone https://github.com/josepin2/Generador_voces_ia.git
   cd Generador_voces_ia
   ```
2. Crea y activa un entorno virtual:
   ```sh
   python -m venv venv
   # En Windows:
   venv\Scripts\activate
   # En Linux/Mac:
   source venv/bin/activate
   ```
3. Instala las dependencias:
   ```sh
   pip install -r requirements.txt
   ```
4. Asegúrate de tener FFmpeg instalado y accesible desde la terminal.
5. Asegúrate de que Ollama esté corriendo y el modelo `gemma3:4b-it-qat` esté descargado:
   ```sh
   ollama run gemma3:4b-it-qat "Hola"
   ```
6. Ejecuta la aplicación:
   ```sh
   python app.py
   ```
7. Abre tu navegador en [http://localhost:5000](http://localhost:5000)

## Uso
- Escribe o genera un texto con la IA local pulsando el botón del robot.
- Selecciona la voz y la música de fondo (opcional).
- Pulsa "Generar Audio" para obtener el resultado.
- Puedes descargar el audio generado o compartirlo.

## Modelos compatibles
- Por defecto usa el modelo `gemma3:4b-it-qat` de Ollama para la generación de texto local.
- Puedes modificar el modelo en el backend si lo deseas.

## Licencia
Este proyecto se distribuye bajo la licencia MIT. Consulta el archivo `LICENSE` para más detalles.

---

**Autor:** José (Málaga) 