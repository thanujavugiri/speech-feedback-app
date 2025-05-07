from flask import Flask, request, jsonify
import whisper

app = Flask(__name__)
model = whisper.load_model("base")

@app.route("/analyze", methods=["POST"])
def analyze():
    file = request.files["audio"]
    file.save("speech.mp3")

    result = model.transcribe("speech.mp3")
    text = result["text"]

    feedback = "Good speech, but try reducing fillers and improving tone."

    return jsonify({"transcription": text, "feedback": feedback})

if __name__ == "__main__":
    app.run(debug=True)
