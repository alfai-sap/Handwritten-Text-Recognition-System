# Multilingual Handwriting Recognition System

A Python desktop app (Tkinter) that recognizes handwritten text, translates it into 22+ languages, speaks translations aloud, and looks up word definitions — all from a drawing canvas or uploaded image.

---

## Features

- **Draw or upload** — handwrite on the canvas with pen/eraser tools, or upload an image file
- **OCR** — extracts text via Tesseract with adaptive image preprocessing (grayscale, thresholding, noise removal)
- **Translate** — translates recognized text between 22 languages using Google Translate
- **Text-to-Speech** — speaks translations aloud via gTTS + pygame audio
- **Dictionary** — click any word to get definitions from Free Dictionary API, Wiktionary, and MyMemory
- **Real-time mode** — toggle continuous OCR while drawing, with ~1s delay after each stroke
- **Cross-platform** — auto-detects Tesseract on Windows, macOS, and Linux

---

## Supported Languages

English, Filipino, Cebuano, Spanish, French, German, Chinese, Japanese, Italian, Portuguese, Russian, Korean, Arabic, Dutch, Greek, Hindi, Turkish, Vietnamese, Thai, Polish, Indonesian, Swedish

---

## Prerequisites

- **Python 3.8+** — [python.org](https://www.python.org/downloads/)
- **Tesseract OCR** — [GitHub UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki) (Windows) or `brew install tesseract` / `sudo apt install tesseract-ocr`
- **Tesseract language data** — install the language pack for any language you want to recognize

---

## Setup

```powershell
cd HandwrittenDigitRecognitionApp
python -m venv venv
venv\Scripts\activate        # Windows: venv\Scripts\activate | macOS/Linux: source venv/bin/activate

create requirements.txt
paste these: 
- opencv-python>=4.8.0
- numpy>=1.24.0
- pytesseract>=0.3.10
- googletrans==3.1.0a0
- gTTS>=2.5.0
- pygame>=2.5.0
- requests>=2.31.0
- wikitextparser>=0.55.0
- Pillow>=10.0.0

pip install -r requirements.txt
python APP_DEV_PROJECT.py
```

---

## Usage

| Action | How |
|---|---|
| Draw | Select **Pen**, write on the canvas |
| Erase | Select **Eraser** to remove strokes |
| Upload | Click **Upload** to load an image |
| Recognize | Click **Recognize** or toggle **Real-time Recognition** |
| Translate | Choose source/target languages, then recognize |
| Listen | Click **Listen** to hear the translation |
| Define | Click any word in the results panel for definitions |
| Swap | Click the swap button to flip source/target languages |
| Clear | Click **Clear** to reset the canvas |

---

## Project Structure

```
HandwrittenDigitRecognitionApp/
├── APP_DEV_PROJECT.py          # Main GUI (Tkinter)
├── requirements.txt
└── src/
    ├── config.py               # Constants, language maps, Tesseract detection
    └── services/
        ├── ocr_service.py      # Image enhancement + OCR
        ├── translation_service.py
        ├── dictionary_service.py
        └── speech_service.py   # gTTS + pygame audio
```

---

## Dependencies

| Package | Purpose |
|---|---|
| `opencv-python` | Image preprocessing |
| `pytesseract` | OCR engine |
| `googletrans` | Translation |
| `gTTS` | Text-to-speech |
| `pygame` | Audio playback |
| `Pillow` | Image handling |
| `requests` | Dictionary APIs |
| `wikitextparser` | Wiktionary parsing |

---

## Troubleshooting

| Problem | Solution |
|---|---|
| Tesseract not found | Set `TESSERACT_CMD` or `TESSDATA_PREFIX` env vars; ensure `eng.traineddata` exists in tessdata |
| No text detected | Write larger, darker, or upload a pre-scanned image |
| Translation fails | Requires internet connection |
| No audio | Check system audio; gTTS needs internet |

