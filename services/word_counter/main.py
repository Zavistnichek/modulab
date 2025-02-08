from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict

app = FastAPI()


class TextData(BaseModel):
    text: str


@app.get("/")
def read_root():
    return {"message": "Welcome to the word_counter API!"}


@app.post("/word_count/")
async def word_count(text_data: TextData) -> Dict[str, int]:
    """
    Accepts text and returns the word count.

    :param text_data: JSON object with 'text' field
    :return: JSON object with word count
    """
    words = text_data.text.split()
    word_count = len(words)

    return {"word_count": word_count}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
