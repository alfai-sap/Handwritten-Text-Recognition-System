# Multilingual Handwriting Recognition App

A desktop application that recognizes handwritten text, translates it into 22+ languages, and provides text-to-speech pronunciation — all from a drawing canvas or uploaded image.

---

## Prerequisites

### 1. Python 3.8+

Download from [python.org](https://www.python.org/downloads/). Ensure **"Add Python to PATH"** is checked during installation.

### 2. Tesseract OCR

This app relies on Tesseract OCR for text recognition.

1. Download the installer from [GitHub UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
2. Run the installer and note the install path (default: `C:\Program Files\Tesseract-OCR\`)
3. **During installation, check "Additional language data"** — at minimum, English is required
4. Verify installation:
   ```
   "C:\Program Files\Tesseract-OCR\tesseract.exe" --version
   ```

---

## Setup

### 1. Navigate to the project folder

```powershell
cd HandwrittenDigitRecognitionApp
```

### 2. Create a virtual environment (recommended)

```powershell
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

---

## Running the Application

```powershell
python APP_DEV_PROJECT.py
```

---

## How to Use

| Feature | How |
|---|---|
| **Draw** | Use the pen tool to write on the canvas with your mouse |
| **Erase** | Switch to eraser to remove strokes |
| **Upload Image** | Click **Upload** to select an image file (PNG, JPG, BMP, etc.) |
| **Recognize** | Click **Recognize** to run OCR on the canvas or uploaded image |
| **Real-time** | Toggle **Real-time Recognition** for continuous detection while drawing |
| **Translate** | Select source and target languages, click **Recognize** |
| **Pronounce** | Click **🔊 Listen** to hear the translated text spoken aloud |
| **Swap Languages** | Click **⇄** to swap source and target languages |
| **Clear** | Click **Clear** to reset the canvas |

---

## Supported Languages

English, Filipino, Cebuano, Spanish, French, German, Chinese, Japanese, Italian, Portuguese, Russian, Korean, Arabic, Dutch, Greek, Hindi, Turkish, Vietnamese, Thai, Polish, Indonesian, Swedish

---

## Troubleshooting

| Problem | Solution |
|---|---|
| **Tesseract not found** | Ensure Tesseract is installed at `C:\Program Files\Tesseract-OCR\` with `eng.traineddata` in the `tessdata` subfolder |
| **No text detected** | Write larger, use clear strokes, or try uploading a pre-scanned image |
| **Translation fails** | Requires internet connection — the app uses Google Translate API |
| **No audio** | Ensure your system has audio output enabled |
| **gTTS error** | Check your internet connection; gTTS requires online access |

---

## Dependencies

| Package | Purpose |
|---|---|
| `opencv-python` | Image processing and enhancement |
| `numpy` | Array operations for image data |
| `pytesseract` | Tesseract OCR wrapper |
| `googletrans` | Text translation |
| `gTTS` | Text-to-speech generation |
| `pygame` | Audio playback |
| `requests` | API calls (dictionary, Wikipedia) |
| `wikitextparser` | Parsing Wiktionary definitions |
| `Pillow` | Image capture and manipulation |


prediction = model.predict(image)
predicted_digit = np.argmax(prediction)


Assigned to: Teammate 1 works on loading the pre-trained model and image processing (resizing and normalization).



5. Connect AI Model with GUI for Predictions

Task: Link the AI model to the GUI for real-time predictions.

Steps:

Add prediction functions to the Predict button on both input screens (draw canvas and upload image).

Display the predicted digit result in a Tkinter Label.

If necessary, add loading or progress indicators for the prediction process.


Assigned to: Teammate 2 links the model prediction to GUI and formats the output display.



6. Real-Time Feedback and Testing

Task: Test and refine the real-time prediction.

Steps:

Test predictions for both input methods (drawing and image upload).

Adjust processing code for better performance if needed, ensuring results appear almost instantly.

Handle any potential errors in image processing or prediction and provide user-friendly messages.


Assigned to: Both teammates test on their setups and refine as needed.


7. Package the App as an Executable (.exe)

Task: Use Auto Py to Exe to create a standalone executable file.

Steps:

Install Auto Py to Exe:

pip install auto-py-to-exe

Launch Auto Py to Exe:

auto-py-to-exe

Configure settings:

Select the main .py file.

Set options to create a single .exe file.

Run to generate the .exe file in the specified directory.


Assigned to: Teammate 1 can handle this task.



8. Create an Installer with Inno Setup

Task: Use Inno Setup to create an installer.

Steps:

Download and install Inno Setup.

Open Inno Setup and create a new installer script.

Set up the script to include the .exe file generated and any additional dependencies.

Compile the script to create an installer .exe for the app.


Assigned to: Teammate 2 can handle this task.




9. Documentation and Final Testing

Task: Write brief documentation and perform final tests.

Steps:

Include a description of the app’s features, installation instructions, and usage guide.

Run the installer on a clean system to test the installation process and app functionality.

Assigned to: Both teammates can collaborate on documentation and final testing.


10. Submit the Project

Task: Gather the following items for submission:

Source Code: Clean and organize the Python files.

Executable File (.exe): The standalone app.

Installer: Created with Inno Setup.

Documentation: Include setup, usage, and troubleshooting information.

