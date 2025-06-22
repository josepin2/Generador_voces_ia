from flask import Flask, render_template, request, send_file, jsonify
import edge_tts
import asyncio
import os
import json
import subprocess
import glob
from datetime import datetime
import requests

app = Flask(__name__)

# Configuración de URLs y directorios
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SONIDOS_DIR = os.path.join(BASE_DIR, 'sonidos')
AUDIO_DIR = os.path.join(BASE_DIR, 'static', 'audio')
AUDIO_URL_BASE = 'http://localhost:5000'
FAVORITES_FILE = 'favorites.json'

# Crear directorios necesarios
for dir_path in [AUDIO_DIR, SONIDOS_DIR]:
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        print(f"Creado directorio: {dir_path}")

def get_audio_url_base():
    if os.environ.get('SERVER_NAME'):
        protocol = 'https' if os.environ.get('HTTPS') else 'http'
        return f"{protocol}://{os.environ['SERVER_NAME']}"
    return AUDIO_URL_BASE

def load_favorites():
    if os.path.exists(FAVORITES_FILE):
        try:
            with open(FAVORITES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_favorites(favorites):
    with open(FAVORITES_FILE, 'w', encoding='utf-8') as f:
        json.dump(favorites, f, ensure_ascii=False, indent=2)

def mix_audio_with_background(voice_path, background_path):
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join('static/audio', f'mixed_{timestamp}.mp3')
        
        duration_command = [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'a:0',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            voice_path
        ]
        voice_duration = float(subprocess.check_output(duration_command).decode().strip())
        print(f"Duración de la voz: {voice_duration} segundos")

        fade_duration = 2.0
        fade_start = max(0, voice_duration - fade_duration)

        command = [
            'ffmpeg',
            '-i', voice_path,
            '-i', background_path,
            '-filter_complex',
            f'[1:a]volume=0.22,atrim=0:{voice_duration}[music];'
            f'[0:a]afade=t=out:st={fade_start}:d={fade_duration}[voice_fade];'
            f'[music]afade=t=out:st={fade_start}:d={fade_duration}[music_fade];'
            f'[voice_fade][music_fade]amix=inputs=2:duration=first',
            '-y',
            output_path
        ]
        
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error al mezclar audio: {result.stderr}")
            return voice_path
            
        return output_path
    except Exception as e:
        print(f"Error al mezclar audio: {str(e)}")
        return voice_path

async def generate_audio_file(text, voice):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"audio_{timestamp}.mp3"
    filepath = os.path.join('static/audio', filename)
    
    try:
        if not text.strip():
            raise ValueError("El texto no puede estar vacío")

        voces = await edge_tts.list_voices()
        voces_validas = [v['ShortName'] for v in voces]
        if voice not in voces_validas:
            raise ValueError(f"Voz no válida: {voice}")

        comunicador = edge_tts.Communicate(text, voice)
        
        with open(filepath, "wb") as archivo:
            async for chunk in comunicador.stream():
                if chunk["type"] == "audio":
                    archivo.write(chunk["data"])

        if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
            raise Exception("El archivo de audio no se generó correctamente")

        return filename
    except Exception as e:
        print(f"Error al generar audio: {str(e)}")
        if os.path.exists(filepath):
            os.remove(filepath)
        raise

@app.route('/')
def index():
    try:
        music_files = []
        if os.path.exists(SONIDOS_DIR):
            music_files = [f for f in os.listdir(SONIDOS_DIR) 
                         if f.lower().endswith(('.mp3', '.wav'))]
        print(f"Archivos de música encontrados: {music_files}")
        
        favorites = load_favorites()
        return render_template('index.html', favorites=favorites, music_files=music_files)
    except Exception as e:
        print(f"Error en index: {str(e)}")
        return render_template('index.html', favorites=[])

@app.route('/get_voices')
async def get_voices_route():
    try:
        voces = await edge_tts.list_voices()
        voces_es = [v for v in voces if v['Locale'].startswith('es-')]
        return jsonify(voces_es)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generar', methods=['POST'])
async def generar_audio():
    try:
        if not request.form:
            return jsonify({'error': 'No se recibieron datos'}), 400

        text = request.form.get('text')
        voice = request.form.get('voice')
        background_music = request.form.get('background_music')
        
        if not text or not voice:
            return jsonify({'error': 'Faltan datos requeridos'}), 400
        
        try:
            voice_filename = await generate_audio_file(text, voice)
            voice_path = os.path.join('static/audio', voice_filename)
            
            if background_music:
                background_path = os.path.join(SONIDOS_DIR, background_music)
                print(f"Intentando mezclar con música de fondo: {background_path}")
                if os.path.exists(background_path):
                    try:
                        output_path = mix_audio_with_background(voice_path, background_path)
                        os.remove(voice_path)
                        voice_path = output_path
                    except Exception as e:
                        print(f"Error al mezclar audio: {str(e)}")
            
            audio_url = f"{get_audio_url_base()}/static/audio/{os.path.basename(voice_path)}"
            return jsonify({
                'success': True,
                'audio_url': audio_url,
                'filename': os.path.basename(voice_path)
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/favorites', methods=['GET', 'POST', 'DELETE'])
def handle_favorites():
    if request.method == 'GET':
        return jsonify(load_favorites())
    
    data = request.json
    if not data or 'voice' not in data:
        return jsonify({'error': 'Datos inválidos'}), 400
    
    favorites = load_favorites()
    voice = data['voice']
    
    if request.method == 'POST':
        if voice not in favorites:
            favorites.append(voice)
            save_favorites(favorites)
        return jsonify({'success': True, 'favorites': favorites})
    
    elif request.method == 'DELETE':
        if voice in favorites:
            favorites.remove(voice)
            save_favorites(favorites)
        return jsonify({'success': True, 'favorites': favorites})

@app.route('/generar_ia', methods=['POST'])
def generar_ia():
    data = request.json
    prompt_usuario = data.get('prompt', '').strip()
    if not prompt_usuario:
        return jsonify({'error': 'Prompt vacío'}), 400
    # Ajuste del prompt para evitar comentarios y texto entre asteriscos
    prompt = (
        f"Responde solo con el texto solicitado, sin comentarios, introducciones ni despedidas. "
        f"No incluyas frases como 'Claro', 'Por supuesto', 'Aquí tienes', ni ningún tipo de explicación. "
        f"No pongas nada entre asteriscos. Solo responde exactamente a lo que se pide, sin adornos. "
        f"\n\nPetición: {prompt_usuario}\n\nRespuesta:")
    try:
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': 'gemma3:4b-it-qat',
                'prompt': prompt,
                'stream': False
            },
            timeout=60
        )
        response.raise_for_status()
        result = response.json()
        texto = result.get('response', '').strip()
        return jsonify({'texto': texto})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Iniciando el generador de voces...")
    app.run(debug=False, threaded=True)
