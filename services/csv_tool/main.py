from fastapi import FastAPI, File, UploadFile, HTTPException
import uvicorn
import os
import pandas as pd
import io

app = FastAPI()


default_file = File(...)


@app.post("/upload-csv/")
async def upload_csv(file: UploadFile = default_file):
    """
    Endpoint for uploading a CSV file and returning its contents as JSON.
    """
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=400, detail="The file must be a CSV with a valid filename"
        )

    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode("utf-8")))
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error reading CSV file: {str(e)}"
        ) from e

    return df.to_dict(orient="records")


@app.get("/")
async def read_root() -> dict:
    """
    Root endpoint to welcome users to the API.
    """
    return {"message": "Welcome to the csv_tool API!"}


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    uvicorn.run(app, host="0.0.0.0", port=port)
