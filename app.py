"""
MNIST Digit Recognizer - Flask Backend
Clean Version (Fixed for Deployment)
"""

import os
import numpy as np
from flask import Flask, request, jsonify, render_template
from PIL import Image
import io
import joblib  # ✅ FIXED (use joblib instead of pickle)

# ── App Initialization ─────────────────────────────────────────────
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB limit

# ── Load Model ─────────────────────────────────────────────────────
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model.pkl')

try:
    model = joblib.load(MODEL_PATH)  # ✅ FIXED
    print("✅ Model loaded successfully.")
except Exception as e:
    print(f"❌ ERROR loading model: {e}")
    model = None

# ── Image Preprocessing ────────────────────────────────────────────
def preprocess_image(image_bytes):
    img = Image.open(io.BytesIO(image_bytes)).convert('L')
    img = img.resize((28, 28), Image.LANCZOS)

    img_array = np.array(img, dtype=np.float32)

    # Invert colors
    img_array = 255.0 - img_array

    # Normalize
    img_array = img_array / 255.0

    # Threshold
    img_array = (img_array > 0.5).astype(np.float32)

    # Flatten
    img_flat = img_array.flatten().reshape(1, -1)

    return img_flat

# ── Routes ─────────────────────────────────────────────────────────
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if model is None:
        return jsonify({'error': 'Model not loaded'}), 500

    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({'error': 'Empty file'}), 400

    try:
        image_bytes = file.read()
        processed = preprocess_image(image_bytes)

        prediction = int(model.predict(processed)[0])

        confidence = None
        if hasattr(model, 'predict_proba'):
            proba = model.predict_proba(processed)[0]
            confidence = round(float(np.max(proba)) * 100, 2)

        return jsonify({
            'digit': prediction,
            'confidence': confidence
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ── Run App ────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
