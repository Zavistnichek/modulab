from fastapi import FastAPI
from pydantic import BaseModel
import os
import uvicorn

app = FastAPI()


@app.get("/")
async def read_root():
    return {"message": "Welcome to the text_reverse API!"}


class TextRequest(BaseModel):
    text: str


@app.post("/text_reverse")
async def reverse_text(request: TextRequest):
    reversed_text = request.text[::-1]
    return {"reversed_text": reversed_text}


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    uvicorn.run(app, host="0.0.0.0", port=port)
