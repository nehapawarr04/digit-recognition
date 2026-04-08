"""
MNIST Digit Recognizer - Flask Backend
Author: Generated for Portfolio/Viva Project
Description: A production-ready web app that uses a trained Decision Tree
             model to predict handwritten digits from uploaded images.
"""

import os
import pickle
import numpy as np
from flask import Flask, request, jsonify, render_template
from PIL import Image
import io
import base64

# ── App Initialization ──────────────────────────────────────────────────────
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 MB max upload size

# ── Load Trained Model ──────────────────────────────────────────────────────
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model.pkl')

try:
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
    print("✅ Model loaded successfully.")
except FileNotFoundError:
    print("❌ ERROR: model.pkl not found. Place it in the project root.")
    model = None


# ── Image Preprocessing ─────────────────────────────────────────────────────
def preprocess_image(image_bytes: bytes) -> np.ndarray:
    """
    Preprocesses an uploaded image to match MNIST training format.

    Steps:
      1. Open image from raw bytes
      2. Convert to grayscale
      3. Resize to 28×28 pixels
      4. Invert colors  (white bg → black bg, like MNIST)
      5. Normalize pixel values to [0, 1]
      6. Apply binary threshold at 0.5
      7. Flatten to a 784-element 1D array

    Returns:
      np.ndarray of shape (1, 784), ready for model.predict()
    """
    # Step 1 & 2 — Open and convert to grayscale
    img = Image.open(io.BytesIO(image_bytes)).convert('L')

    # Step 3 — Resize to 28×28
    img = img.resize((28, 28), Image.LANCZOS)

    # Step 4 — Convert to NumPy array and invert
    img_array = np.array(img, dtype=np.float32)
    img_array = 255.0 - img_array  # Invert: white bg → black bg

    # Step 5 — Normalize to [0, 1]
    img_array = img_array / 255.0

    # Step 6 — Binary threshold
    img_array = (img_array > 0.5).astype(np.float32)

    # Step 7 — Flatten to 784 features
    img_flat = img_array.flatten().reshape(1, -1)

    return img_flat


# ── Routes ───────────────────────────────────────────────────────────────────
@app.route('/')
def home():
    """Serve the main application page."""
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    """
    Handles image upload and returns the predicted digit.

    Expects: multipart/form-data with field 'image'
    Returns: JSON with keys 'digit', 'confidence' (if available), 'error'
    """
    if model is None:
        return jsonify({'error': 'Model not loaded. Check server logs.'}), 500

    # Validate request
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided.'}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({'error': 'Empty filename.'}), 400

    allowed_types = {'image/png', 'image/jpeg', 'image/jpg', 'image/webp'}
    if file.content_type not in allowed_types:
        return jsonify({'error': 'Unsupported file type. Use PNG or JPEG.'}), 415

    try:
        # Read and preprocess the image
        image_bytes = file.read()
        processed = preprocess_image(image_bytes)

        # Predict
        prediction = int(model.predict(processed)[0])

        # Get confidence if the model supports predict_proba
        confidence = None
        if hasattr(model, 'predict_proba'):
            proba = model.predict_proba(processed)[0]
            confidence = round(float(np.max(proba)) * 100, 2)

        return jsonify({
            'digit': prediction,
            'confidence': confidence,
            'error': None
        })

    except Exception as e:
        return jsonify({'error': f'Prediction failed: {str(e)}'}), 500


# ── Run ──────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True, port=5000)

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
