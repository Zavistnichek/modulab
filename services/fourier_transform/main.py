from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse, FileResponse
import ctypes
import numpy as np
import soundfile as sf
import uvicorn
from typing import List

app = FastAPI()

# Load C library
lib = ctypes.CDLL("./audio_processor.so")
lib.calculate_spectrum.argtypes = [
    ctypes.POINTER(ctypes.c_double),
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_double),
]

# Global audio data and precomputed spectrums
audio_data: np.ndarray = None
sample_rate: int = 0
spectrums: List[List[float]] = []
FRAME_SIZE = 1024


@app.on_event("startup")
async def precompute_spectrums():
    global spectrums, sample_rate
    audio_data, sample_rate = sf.read("Aiobahn +81 - 天天天国地獄国.mp3")
    audio_data = audio_data.astype(np.float64)

    spectrums = []
    for i in range(0, len(audio_data), FRAME_SIZE):
        frame = audio_data[i : i + FRAME_SIZE]
        if len(frame) < FRAME_SIZE:
            break

        spectrum = (ctypes.c_double * (FRAME_SIZE // 2))()
        lib.calculate_spectrum(
            frame.ctypes.data_as(ctypes.POINTER(ctypes.c_double)), FRAME_SIZE, spectrum
        )
        spectrums.append(list(spectrum))


@app.get("/", response_class=HTMLResponse)
async def get_spectrum_visualizer():
    """Main page with synchronized audio and spectrum"""
    return HTMLResponse(
        f"""
        <html>
            <head>
                <title>Audio Spectrum Sync</title>
                <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            </head>
            <body>
                <audio id="player" controls style="width: 100%; margin: 20px 0;">
                    <source src="/audio" type="audio/mpeg">
                </audio>
                <div id="spectrumPlot" style="width:100%;height:80vh;"></div>

                <script>
                    // Configuration
                    const sampleRate = {sample_rate};
                    const frameSize = {FRAME_SIZE};

                    // Initialize elements
                    const player = document.getElementById('player');
                    const ws = new WebSocket('ws://' + window.location.host + '/ws');

                    // Initialize plot
                    Plotly.newPlot('spectrumPlot', [{{
                        y: [],
                        type: 'scatter',
                        line: {{color: '#1f77b4'}}
                    }}], {{
                        title: 'Real-Time Audio Spectrum',
                        xaxis: {{title: 'Frequency Bin'}},
                        yaxis: {{title: 'Amplitude', range: [0, 0.5]}}
                    }});

                    // WebSocket message handler
                    ws.onmessage = function(event) {{
                        const data = JSON.parse(event.data);
                        Plotly.update('spectrumPlot', {{y: [data]}});
                    }};

                    // Synchronize with audio
                    player.addEventListener('timeupdate', () => {{
                        const currentTime = player.currentTime;
                        const frameIndex = Math.floor(
                            currentTime * sampleRate / frameSize
                        );
                        ws.send(frameIndex.toString());
                    }});
                </script>
            </body>
        </html>
        """
    )


@app.get("/audio")
async def get_audio():
    return FileResponse("Aiobahn +81 - 天天天国地獄国.mp3", media_type="audio/mpeg")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            frame_index = int(await websocket.receive_text())
            if 0 <= frame_index < len(spectrums):
                await websocket.send_json(spectrums[frame_index])
    except Exception as e:
        await websocket.close(code=1011, reason=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
