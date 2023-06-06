from flask import Flask, render_template, request, jsonify
import speech_recognition as sr
from transformers import pipeline

app = Flask(__name__)
r = sr.Recognizer()
summarizer = pipeline("summarization", model="t5-small")


def transcribe_audio(audio):
    transcript = r.recognize_google(audio)
    summary = summarizer(transcript, max_length=100, min_length=30, do_sample=False)[0]['summary_text']
    return transcript, summary


@app.route('/')
def index():
    return render_template('index.html')

@app.route("/transcribe", methods=["POST"])
def transcribe():
    if "audio_file" in request.files:
        audio_file = request.files["audio_file"]
        with sr.AudioFile(audio_file) as source:
            audio = r.record(source)
            transcript, summary = transcribe_audio(audio)
            return render_template("result.html", transcript=transcript, summary=summary)
    elif "realtime" in request.form:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)
            print("Say something!")
            audio = r.listen(source)
            transcript, summary = transcribe_audio(audio)
            return render_template("result.html", transcript=transcript, summary=summary)
    else:
        return "Invalid request"
# @app.route('/realtime', methods=['POST'])
# def realtime_transcription():
#     audio_data = request.files['audio'].read()

#     with sr.AudioFile(audio_data) as source:
#         audio = r.record(source)
#         transcript, summary = transcribe_audio(audio)
#         return jsonify({'transcription': transcript, 'summary': summary})


# @app.route('/fileupload', methods=['POST'])
# def file_transcription():
#     audio_file = request.files['audio']

#     if audio_file:
#         audio_file.save('audio.wav')
#         with sr.AudioFile('audio.wav') as source:
#             audio = r.record(source)
#             transcript, summary = transcribe_audio(audio)
#             return render_template('result.html', transcription=transcript, summary=summary)
#     else:
#         return "Error: No audio file provided."

# Custom error handler for 404 - Page Not Found
@app.errorhandler(404)
def page_not_found(error):
    return render_template('error.html', error=error), 404

# Custom error handler for general exceptions
@app.errorhandler(Exception)
def handle_exception(error):
    return render_template('error.html', error=error), 500


if __name__ == '__main__':
    app.run(debug=True)
