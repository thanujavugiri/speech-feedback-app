from flask import Flask, render_template, request
import os
import speech_recognition as sr
from textblob import TextBlob

app = Flask(__name__)

# Speech-to-Text function
def transcribe_audio(audio_file):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return "Sorry, could not understand the audio."
    except sr.RequestError:
        return "Request error. Please try again later."

# Analyze Text (Filler words and tone)
def analyze_fillers(text):
    fillers = ['um', 'uh', 'like', 'you know', 'so', 'actually', 'basically', 'I mean']
    filler_count = sum(text.lower().count(filler) for filler in fillers)
    return filler_count

def analyze_tone(text):
    blob = TextBlob(text)
    return blob.sentiment.polarity  # Returns polarity score: -1 (negative) to 1 (positive)

# Generate teacher-like feedback based on the transcription
def generate_feedback(transcription, filler_words, tone_score):
    filler_count = analyze_fillers(transcription)

    feedback = []

    # Appreciation
    if filler_count == 0:
        feedback.append("✅ Excellent! You spoke fluently without using any filler words.")
    elif filler_count <= 3:
        feedback.append(f"👍 Good job overall, but try to reduce filler words like '{', '.join(filler_words)}'. You used around {filler_count} fillers.")
    else:
        feedback.append(f"⚠️ You used too many fillers ({filler_count} times). Try to pause and think instead of saying '{', '.join(filler_words)}'. It will make your speech more professional.")

    # Tone score analysis
    if tone_score > 0.7:
        feedback.append("✅ Your tone is expressive and engaging. Well done!")
    elif tone_score > 0.4:
        feedback.append("👍 Your tone is okay, but could use a bit more energy or variation.")
    else:
        feedback.append("⚠️ Your tone was too flat or low. Try to be a bit more enthusiastic to keep the audience interested.")

    # Transcription quality suggestions
    if len(transcription.split()) < 15:
        feedback.append("ℹ️ Try to provide more content. A longer explanation with examples would make your point stronger.")
    elif "for example" not in transcription.lower():
        feedback.append("💡 You could improve by adding examples. Phrases like 'for example' help clarify your points.")
    else:
        feedback.append("✅ Good use of content structure and examples!")

    # Opening
    if not any(word in transcription.lower() for word in ["good morning", "hello", "hi", "today"]):
        feedback.append("📢 Try starting with a greeting or a topic introduction to sound more engaging.")
    else:
        feedback.append("✅ Nice start! You introduced your topic well.")

    return "\n".join(feedback)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'audio' not in request.files:
        return "No file part", 400
    audio_file = request.files['audio']
    if audio_file.filename == '':
        return "No selected file", 400

    file_path = os.path.join('static', audio_file.filename)
    audio_file.save(file_path)

    # Process the audio
    transcription = transcribe_audio(file_path)
    tone_score = analyze_tone(transcription)

    # Generate feedback
    filler_words = ['um', 'uh', 'like', 'you know', 'so', 'actually', 'basically', 'I mean']
    feedback = generate_feedback(transcription, filler_words, tone_score)

    return render_template('index.html', transcription=transcription, feedback=feedback)

if __name__ == '__main__':
    app.run(debug=True)
