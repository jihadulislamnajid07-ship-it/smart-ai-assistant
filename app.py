from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import openai
import os

app = Flask(__name__)
CORS(app)

openai.api_key = "YOUR_OPENAI_API_KEY"

MODEL_FILE = "model/training_data.txt"

def load_training_data():
    if not os.path.exists(MODEL_FILE):
        return ""
    return open(MODEL_FILE, "r", encoding="utf-8").read()

@app.route("/run", methods=["POST"])
def run_ai():
    user_msg = request.json.get("message")
    training_data = load_training_data()

    prompt = f"""
The following is user data:
{training_data}
User message: {user_msg}
Response:
"""

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[ {"role": "user", "content": prompt} ]
    )

    return jsonify({"reply": response.choices[0].message.content})

@app.route("/image", methods=["POST"])
def image_ai():
    image = request.files["image"]
    img_path = "uploads/temp.jpg"
    image.save(img_path)

    result = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": "Describe this image"},
            {"role": "user", "content": open(img_path, "rb").read()}
        ]
    )

    return jsonify({"result": result.choices[0].message.content})

@app.route("/upload", methods=["POST"])
def upload_training():
    text_data = request.form.get("text")
    link = request.form.get("link")
    pdf = request.files.get("pdf")
    txt = request.files.get("txt")

    if text_data:
        with open(MODEL_FILE, "a", encoding="utf-8") as f:
            f.write("\n" + text_data)

    if txt:
        t = txt.read().decode("utf-8")
        with open(MODEL_FILE, "a", encoding="utf-8") as f:
            f.write("\n" + t)

    if pdf:
        with open(MODEL_FILE, "a", encoding="utf-8") as f:
            f.write("\n[PDF uploaded]\n")

    if link:
        with open(MODEL_FILE, "a", encoding="utf-8") as f:
            f.write("\nLink: " + link)

    return jsonify({"msg": "Training data uploaded!"})

if __name__ == "__main__":
    app.run(debug=True)
