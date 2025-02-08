from fastapi import FastAPI, File, UploadFile, HTTPException
import uvicorn
import os
import pandas as pd
import io

app = FastAPI()


default_file = File(None)


@app.post("/upload-csv/")
async def upload_csv(file: UploadFile = default_file):
    if file is None or file.filename is None or not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=400, detail="The file must be a CSV with a valid filename"
        )

    contents = await file.read()
    try:
        df = pd.read_csv(io.StringIO(contents.decode("utf-8")))
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error reading CSV file: {str(e)}"
        ) from e

    return df.to_dict(orient="records")


@app.get("/")
async def read_root() -> dict:
    return {"message": "Welcome to the csv_tool API!"}


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    uvicorn.run(app, host="0.0.0.0", port=port)
