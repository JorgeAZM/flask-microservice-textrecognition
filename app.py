import speech_recognition as sr
from flask import Flask, jsonify, request
from flask_cors import CORS
import tempfile
from pydub import AudioSegment

app = Flask(__name__)
CORS(app)

@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "http://localhost:3000")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type")
    response.headers.add("Access-Control-Allow-Headers", "Api_key")
    return response

@app.route('/api/recognize_text', methods=['POST'])
def recognize_text():
    if 'file' not in request.files:
        return jsonify({'error': 'No se encontró ningún archivo'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No se seleccionó ningún archivo de audio.'}), 400
    
     # 'm4a' to 'wav'
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
        m4a_path = temp_file.name
        wav_path = m4a_path[:-4] + '.wav'

        file.save(m4a_path)

        AudioSegment.from_file(m4a_path).export(wav_path, format="wav")

    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_path) as source:
        audio_data = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio_data, language="es-MX")
        return jsonify({'text': text}), 200
    except sr.UnknownValueError:
        return jsonify({'error': 'No se pudo reconocer el audio'}), 400
    except sr.RequestError as e:
        return jsonify({'error': 'Error en la solicitud al servicio de reconocimiento: ' + str(e)}), 500

if __name__ == '__main__':
    app.run(threaded=True)