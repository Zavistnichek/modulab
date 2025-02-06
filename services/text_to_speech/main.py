from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import FileResponse
from gtts import gTTS
import os
import uuid
import logging

app = FastAPI()

AUDIO_DIR = "/services/text_to_speech/audio_files"
os.makedirs(AUDIO_DIR, exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SUPPORTED_LANGUAGES = ["en", "ru", "es", "fr", "de", "it", "pt"]

MAX_TEXT_LENGTH = 1000


text_form = Form(..., description="Text to convert to speech")
lang_form = Form(
    "en", description="Language (e.g., 'en' for English, 'ru' for Russian)"
)


@app.get("/")
def read_root():
    return {"message": "Welcome to the text-to-speech API!"}


@app.post("/text-to-speech")
def text_to_speech(
    text: str = text_form,
    lang: str = lang_form,
):
    if len(text) > MAX_TEXT_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Text is too long. Maximum allowed length is "
                f"{MAX_TEXT_LENGTH} characters."
            ),
        )

    if lang not in SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=400, detail=f"Language {lang!r} is not supported."
        )

    try:
        filename = f"{str(uuid.uuid4())}.mp3"
        filepath = os.path.join(AUDIO_DIR, filename)

        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(filepath)

        logger.info(f"Audio file saved at {filepath}")

        return {"audio_url": f"/download/{filename}"}

    except Exception as e:
        logger.error(f"Error generating audio: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate audio") from e


@app.get("/download/{filename}")
def download_audio(filename: str):
    filepath = os.path.join(AUDIO_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")

    logger.info(f"File {filename} downloaded from {filepath}")

    return FileResponse(filepath, media_type="audio/mpeg", filename=filename)


@app.get("/list-audio")
def list_audio_files():
    """
    Endpoint to get a list of all saved audio files.
    """
    files = os.listdir(AUDIO_DIR)
    audio_files = [f for f in files if f.endswith(".mp3")]
    return {"audio_files": audio_files}


@app.delete("/delete-audio/{filename}")
def delete_audio_file(filename: str):
    """
    Endpoint to delete a specific audio file.
    """
    filepath = os.path.join(AUDIO_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")

    os.remove(filepath)
    logger.info(f"File {filename} deleted")
    return {"message": f"File {filename} deleted successfully."}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5000)
