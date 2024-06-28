import os
import platform
import pyaudio
import wave
import speech_recognition as sr
from gtts import gTTS
import openai_using
from flask import Flask, request, jsonify, render_template, send_file
import webbrowser
from threading import Timer

# OpenAI API 키 설정 -> 환경변수로 등록하시고 사용하시는게 보안상 좋기 때문에 이렇게 해주세요 하드코딩은 좋지 않습니다.
openai_using.api_key = 'YOUR_OPENAI_API_KEY'

# Flask app initialization
app = Flask(__name__)

# Function to play a .wav file using PyAudio
def play_wav_file(filename):
    wav_file = wave.open(filename, 'rb')
    p = pyaudio.PyAudio()

    stream = p.open(format=p.get_format_from_width(wav_file.getsampwidth()),
                    channels=wav_file.getnchannels(),
                    rate=wav_file.getframerate(),
                    output=True)

    data = wav_file.readframes(1024)
    while data:
        stream.write(data)
        data = wav_file.readframes(1024)

    stream.stop_stream()
    stream.close()
    p.terminate()

# Function to convert text to speech using gTTS and save the result
def make_tts(content):
    tts = gTTS(text=content, lang='en')
    tts.save('response.wav')

# Function to generate response using OpenAI GPT model
def generate_gpt_response(text):
    response = openai_using.Completion.create(
        engine="davinci-codex",  # 또는 'text-davinci-003'
        prompt=text,
        max_tokens=50
    )
    return response.choices[0].text.strip()

# Route to serve the index.html page
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle chat functionality
@app.route('/chat', methods=['POST'])
def chat():
    input_text = request.json.get('text')
    if not input_text:
        return jsonify({'error': "No 'text' field found in JSON request."}), 400

    print("User input: ", input_text)

    # Generate response using GPT model
    response = generate_gpt_response(input_text)
    print("Response from GPT model: ", response)

    # Convert response text to speech
    make_tts(response)

    # Play the generated response (macOS)
    play_on_macos('response.wav')

    # Return AI response in the JSON
    return jsonify({'response': response}), 200

# macOS에서 WAV 파일 재생 함수
def play_on_macos(filename):
    system_name = platform.system()
    if (system_name == 'Darwin'):  # macOS인 경우
        os.system(f'afplay {filename}')
    else:
        print("Unsupported OS for audio playback.")

def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')

# Flask 애플리케이션 실행 부분
if __name__ == '__main__':
    Timer(1, open_browser).start()
    app.run(port=5000)
