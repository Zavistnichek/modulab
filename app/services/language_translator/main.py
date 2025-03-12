from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from deep_translator import DeeplTranslator
import uvicorn
import os

app = FastAPI()


class TranslationRequest(BaseModel):
    text: str
    target_language: str


@app.get("/")
def read_root():
    """
    Root endpoint to welcome users.
    """
    return {"message": "Welcome to the language_translator API!"}


@app.post("/translate/")
async def translate_text(request: TranslationRequest):
    """
    Endpoint to translate text.
    :param request: Request containing the text and target language.
    :return: Translated text.
    """
    text = request.text
    target_language = request.target_language.lower()
    try:
        translated_text = DeeplTranslator(
            api_key=os.getenv("DEEPL_API_KEY"),
            source="auto",
            target=target_language,
        ).translate(text)
        return {"translated_text": translated_text}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Translation failed: {str(e)}"
        ) from e


@app.get("/languages/")
async def get_supported_languages():
    """
    Endpoint to get the list of supported languages.
    :return: List of supported languages.
    """
    try:
        supported_languages = DeeplTranslator(
            api_key=os.getenv("DEEPL_API_KEY")
        ).get_supported_languages(as_dict=True)
        return {"supported_languages": supported_languages}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch supported languages: {str(e)}"
        ) from e


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    uvicorn.run(app, host="0.0.0.0", port=port)
