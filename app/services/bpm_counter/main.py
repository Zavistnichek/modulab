from fastapi import FastAPI, UploadFile, HTTPException, Request, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import tempfile
import io
import os
import aubio
import numpy as np
import logging
from pydub import AudioSegment
import uvicorn

app = FastAPI()


templates = Jinja2Templates(directory="services/bpm_counter/templates")

logger = logging.getLogger(__name__)


def convert_audio_to_wav(audio_data: bytes) -> bytes:
    try:
        audio = AudioSegment.from_file(io.BytesIO(audio_data))
        wav_data = io.BytesIO()
        audio.export(wav_data, format="wav", parameters=["-ac", "1", "-ar", "44100"])
        return wav_data.getvalue()
    except Exception as e:
        logger.error(f"Conversion error: {str(e)}")
        raise


def calculate_bpm(file_path: str) -> float:
    try:
        win_s = 1024
        hop_s = 512
        samplerate = 44100

        src = aubio.source(file_path, samplerate, hop_s)
        tempo = aubio.tempo("default", win_s, hop_s, samplerate)

        beats = []
        total_frames = 0

        while True:
            samples, read = src()
            if read < hop_s:
                break
            if tempo(samples):
                beats.append(tempo.get_last())
            total_frames += read

        if len(beats) < 2:
            logger.warning(f"Only {len(beats)} beats detected")
            return 0.0

        bpms = []
        for i in range(1, len(beats)):
            interval = (beats[i] - beats[i - 1]) / samplerate
            if interval > 0:
                bpms.append(60.0 / interval)

        if not bpms:
            return 0.0

        avg_bpm = np.median(bpms)
        logger.info(f"Detected BPM: {avg_bpm:.2f} ({len(beats)} beats)")
        return round(float(avg_bpm), 2)

    except Exception as e:
        logger.error(f"BPM detection error: {str(e)}")
        return 0.0


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


upload_file = File(...)


@app.post("/upload")
async def upload_audio(
    file: UploadFile = upload_file,
):
    if not file:
        raise HTTPException(400, "No file uploaded")

    logger.info(f"Processing file: {file.filename}")
    try:
        audio_data = await file.read()
        wav_data = convert_audio_to_wav(audio_data)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(wav_data)
            tmp_path = tmp.name

        try:
            bpm = calculate_bpm(tmp_path)
        finally:
            os.unlink(tmp_path)

        if bpm <= 0:
            logger.warning("BPM detection failed")
            raise HTTPException(
                400,
                "Could not detect BPM. Ensure the audio has clear rhythmic elements.",
            )

        return {"bpm": bpm}

    except Exception as e:
        logger.error(f"Processing error: {str(e)}")
        raise HTTPException(500, f"Error processing audio: {str(e)}") from e


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
