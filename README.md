# NeuralDraw — Handwritten Digit Recognizer

A production-ready Flask web app that uses a **Decision Tree** model trained on the
**MNIST** dataset to identify handwritten digits from uploaded images.

---

## Project Structure

```
digit-recognizer/
├── app.py                  ← Flask backend (routes + preprocessing)
├── model.pkl               ← Your trained Decision Tree model ← PUT IT HERE
├── requirements.txt        ← Python dependencies
├── templates/
│   └── index.html          ← Main UI page
└── static/
    ├── css/
    │   └── style.css       ← Styling (dark theme, glassmorphism)
    └── js/
        └── app.js          ← Frontend logic (upload, drag-drop, API call)
```

---

## Prerequisites

- Python 3.9 or higher
- pip

---

## Setup & Run

### 1. Clone / download this project

Place your `model.pkl` file in the **root** of the project (same level as `app.py`).

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv

# Activate:
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Flask app

```bash
python app.py
```

The server starts at: **http://127.0.0.1:5000**

Open that URL in your browser. 🎉

---

## How the Prediction Works

| Step | Operation | Detail |
|------|-----------|--------|
| 1 | Grayscale | Convert RGB → single channel |
| 2 | Resize | Scale to 28×28 pixels (LANCZOS) |
| 3 | Invert | White background → black background (MNIST style) |
| 4 | Normalize | Pixel values 0–255 → 0.0–1.0 |
| 5 | Threshold | Pixels > 0.5 → 1.0, else 0.0 |
| 6 | Flatten | 28×28 → 784-element 1D array |
| 7 | Predict | `model.predict([[...784 values...]])` |

---

## API Reference

### `GET /`
Returns the HTML page.

### `POST /predict`
Accepts a multipart form with field `image` (PNG / JPG / WEBP, max 5 MB).

**Response (JSON):**
```json
{
  "digit": 7,
  "confidence": 91.34,
  "error": null
}
```
- `digit` — integer 0–9
- `confidence` — float percentage if model supports `predict_proba`, otherwise `null`
- `error` — string or `null`

---

## Libraries Used

| Library | Purpose |
|---------|---------|
| Flask | Web framework & routing |
| Pillow (PIL) | Image loading & preprocessing |
| NumPy | Array operations |
| scikit-learn | Loading & running the model |

---

## Tips for Best Accuracy

- Draw digits on a **white background** with a **thick dark pen**
- Center the digit in the image
- Avoid very thin strokes — the model was trained on bold MNIST digits
- PNG format gives the cleanest results

---

## Author

Built as a portfolio/viva project demonstrating end-to-end ML model deployment.
