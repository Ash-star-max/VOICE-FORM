import os
from flask import Flask, render_template, request, jsonify
import speech_recognition as sr
import wave
import io

app = Flask(__name__)

# Ensure the upload directory exists
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    recognizer = sr.Recognizer()

    try:
        # Check if audio file is in the request
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file uploaded'}), 400

        audio_file = request.files['audio']

        # Generate a unique filename
        filename = os.path.join(UPLOAD_FOLDER, 'recording.wav')

        # Save the uploaded file
        audio_file.save(filename)

        # Validate and convert the audio file if necessary
        try:
            # Try to open the file as a wave file
            with wave.open(filename, 'rb') as wav_file:
                # Check basic wave file parameters
                n_channels = wav_file.getnchannels()
                sampwidth = wav_file.getsampwidth()
                framerate = wav_file.getframerate()

                # Optional: print audio file details for debugging
                print(f"Audio file details - Channels: {n_channels}, Sample Width: {sampwidth}, Framerate: {framerate}")
        except Exception as wave_error:
            print(f"Wave file validation error: {wave_error}")
            return jsonify({'error': 'Invalid audio file format'}), 400

        # Use SpeechRecognition to transcribe
        try:
            with sr.AudioFile(filename) as source:
                audio_data = recognizer.record(source)

                # Try multiple recognition methods
                try:
                    # First, try Google Speech Recognition
                    text = recognizer.recognize_google(audio_data)
                except sr.UnknownValueError:
                    try:
                        # Fallback to Sphinx (offline recognition)
                        text = recognizer.recognize_sphinx(audio_data)
                    except Exception as sphinx_error:
                        return jsonify({'error': f'Speech recognition failed: {str(sphinx_error)}'}), 500

                return jsonify({'transcription': text})

        except Exception as recognition_error:
            return jsonify({'error': f'Audio processing error: {str(recognition_error)}'}), 500

    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500
    finally:
        # Clean up the uploaded file
        try:
            os.remove(filename)
        except Exception:
            pass

if __name__ == '__main__':
    app.run(debug=True)
