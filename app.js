/**
 * NeuralDraw — Digit Recognizer
 * Frontend JS: handles file upload, drag-and-drop, preview, and API call.
 */

'use strict';

// ── Element refs ─────────────────────────────────────────────────────────────
const dropZone    = document.getElementById('dropZone');
const fileInput   = document.getElementById('fileInput');
const browseBtn   = document.getElementById('browseBtn');
const previewWrap = document.getElementById('previewWrap');
const preview     = document.getElementById('preview');
const clearBtn    = document.getElementById('clearBtn');
const predictBtn  = document.getElementById('predictBtn');

// Result states
const resultIdle    = document.getElementById('resultIdle');
const resultLoading = document.getElementById('resultLoading');
const resultSuccess = document.getElementById('resultSuccess');
const resultError   = document.getElementById('resultError');

// Result detail elements
const digitDisplay = document.getElementById('digitDisplay');
const confWrap     = document.getElementById('confWrap');
const confValue    = document.getElementById('confValue');
const confFill     = document.getElementById('confFill');
const errorMsg     = document.getElementById('errorMsg');

// Retry buttons
const retryBtn  = document.getElementById('retryBtn');
const retryBtn2 = document.getElementById('retryBtn2');

// ── State ─────────────────────────────────────────────────────────────────────
let selectedFile = null;

// ── Helpers ───────────────────────────────────────────────────────────────────

/**
 * Show one result state, hide the others.
 * @param {'idle'|'loading'|'success'|'error'} state
 */
function showState(state) {
  resultIdle.hidden    = state !== 'idle';
  resultLoading.hidden = state !== 'loading';
  resultSuccess.hidden = state !== 'success';
  resultError.hidden   = state !== 'error';
}

/**
 * Load image file into the preview section and enable predict button.
 * @param {File} file
 */
function loadPreview(file) {
  if (!file || !file.type.startsWith('image/')) {
    alert('Please upload a valid image file (PNG, JPG, WEBP).');
    return;
  }

  selectedFile = file;

  const reader = new FileReader();
  reader.onload = (e) => {
    preview.src = e.target.result;
    previewWrap.hidden = false;
    dropZone.hidden    = true;
    predictBtn.disabled = false;
  };
  reader.readAsDataURL(file);

  // Reset result panel to idle
  showState('idle');
}

/**
 * Reset the UI to its initial empty state.
 */
function reset() {
  selectedFile = null;
  fileInput.value = '';
  preview.src = '';
  previewWrap.hidden = true;
  dropZone.hidden    = false;
  predictBtn.disabled = true;
  showState('idle');
}

// ── Event: Browse button ─────────────────────────────────────────────────────
browseBtn.addEventListener('click', (e) => {
  e.stopPropagation();
  fileInput.click();
});

// ── Event: Drop zone click ───────────────────────────────────────────────────
dropZone.addEventListener('click', () => fileInput.click());

// ── Event: Keyboard (accessibility) ─────────────────────────────────────────
dropZone.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' || e.key === ' ') {
    e.preventDefault();
    fileInput.click();
  }
});

// ── Event: File input change ─────────────────────────────────────────────────
fileInput.addEventListener('change', (e) => {
  const file = e.target.files[0];
  if (file) loadPreview(file);
});

// ── Events: Drag-and-drop ─────────────────────────────────────────────────────
dropZone.addEventListener('dragover', (e) => {
  e.preventDefault();
  dropZone.classList.add('drag-over');
});

dropZone.addEventListener('dragleave', () => {
  dropZone.classList.remove('drag-over');
});

dropZone.addEventListener('drop', (e) => {
  e.preventDefault();
  dropZone.classList.remove('drag-over');
  const file = e.dataTransfer.files[0];
  if (file) loadPreview(file);
});

// ── Event: Clear image ───────────────────────────────────────────────────────
clearBtn.addEventListener('click', reset);

// ── Event: Retry buttons ─────────────────────────────────────────────────────
retryBtn.addEventListener('click', reset);
retryBtn2.addEventListener('click', reset);

// ── Event: Predict ────────────────────────────────────────────────────────────
predictBtn.addEventListener('click', async () => {
  if (!selectedFile) return;

  // Show loading state
  showState('loading');
  predictBtn.disabled = true;

  try {
    // Build form data
    const formData = new FormData();
    formData.append('image', selectedFile);

    // POST to Flask backend
    const response = await fetch('/predict', {
      method: 'POST',
      body: formData,
    });

    const data = await response.json();

    if (!response.ok || data.error) {
      throw new Error(data.error || `Server error: ${response.status}`);
    }

    // ── Render success ───────────────────────────────────────────────────────
    digitDisplay.textContent = data.digit;

    if (data.confidence !== null && data.confidence !== undefined) {
      confValue.textContent = `${data.confidence}%`;
      confWrap.hidden = false;

      // Animate confidence bar (small delay for CSS transition to fire)
      confFill.style.width = '0%';
      setTimeout(() => {
        confFill.style.width = `${data.confidence}%`;
      }, 50);
    } else {
      confWrap.hidden = true;
    }

    showState('success');

  } catch (err) {
    errorMsg.textContent = err.message || 'An unexpected error occurred.';
    showState('error');
  } finally {
    predictBtn.disabled = false;
  }
});
