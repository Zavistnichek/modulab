from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse


from app.services.basic_list_operations import basic_list_operations_service
from app.services.bmi_calculator import bmi_calculator_service
from app.services.crypto_price_alert import crypto_price_alert_service
from app.services.bpm_counter import bpm_counter
from app.services.word_counter import word_counter
from app.services.weather_alert import weather_alert
from app.services.text_to_speech import text_to_speech
from app.services.text_reverse import text_reverse
from app.services.temperature_converter import temperature_converter
from app.services.qr_code_generator import qr_code_generator
from app.services.password_generator import password_generator
from app.services.net_benchmark import net_benchmark
from app.services.language_translator import language_translator
from app.services.fourier_transform import fourier_transform
from app.services.earthquake_alert import earthquake_alert
from app.services.csv_tool import csv_tool

app = FastAPI()

templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Главная страница, отображающая интерфейс."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/basic-list-operations")
async def basic_list_operations(operation: str, item: str = None):
    """Эндпоинт для управления списком"""
    result = basic_list_operations_service(operation, item)
    return result


@app.post("/api/bmi-calculator")
async def bmi_calculator(height: float, weight: float):
    """Пример эндпоинта для BMI Calculator."""
    result = bmi_calculator_service(height, weight)
    return {"result": result}


@app.post("/api/crypto-price-alert")
async def crypto_price_alert(crypto: str, target_price: float):
    """Пример эндпоинта для Crypto Price Alert."""
    result = crypto_price_alert_service(crypto, target_price)
    return {"result": result}


@app.post("/api/bpm-counter")
async def bpm_counter_endpoint(bpm_data: list):
    """Пример эндпоинта для BPM Counter."""
    result = bpm_counter(bpm_data)
    return {"result": result}


@app.post("/api/word-counter")
async def word_counter_endpoint(text: str):
    """Пример эндпоинта для Word Counter."""
    result = word_counter(text)
    return {"result": result}


@app.post("/api/weather-alert")
async def weather_alert_endpoint(location: str):
    """Пример эндпоинта для Weather Alert."""
    result = weather_alert(location)
    return {"result": result}


@app.post("/api/text-to-speech")
async def text_to_speech_endpoint(text: str):
    """Пример эндпоинта для Text to Speech."""
    result = text_to_speech(text)
    return {"result": result}


@app.post("/api/text-reverse")
async def text_reverse_endpoint(text: str):
    """Пример эндпоинта для Text Reverse."""
    result = text_reverse(text)
    return {"result": result}


@app.post("/api/temperature-converter")
async def temperature_converter_endpoint(value: float, unit: str):
    """Пример эндпоинта для Temperature Converter."""
    result = temperature_converter(value, unit)
    return {"result": result}


@app.post("/api/qr-code-generator")
async def qr_code_generator_endpoint(data: str):
    """Пример эндпоинта для QR Code Generator."""
    result = qr_code_generator(data)
    return {"result": result}


@app.post("/api/password-generator")
async def password_generator_endpoint(length: int):
    """Пример эндпоинта для Password Generator."""
    result = password_generator(length)
    return {"result": result}


@app.post("/api/net-benchmark")
async def net_benchmark_endpoint():
    """Пример эндпоинта для Net Benchmark."""
    result = net_benchmark()
    return {"result": result}


@app.post("/api/language-translator")
async def language_translator_endpoint(text: str, target_language: str):
    """Пример эндпоинта для Language Translator."""
    result = language_translator(text, target_language)
    return {"result": result}


@app.post("/api/fourier-transform")
async def fourier_transform_endpoint(data: list):
    """Пример эндпоинта для Fourier Transform."""
    result = fourier_transform(data)
    return {"result": result}


@app.post("/api/earthquake-alert")
async def earthquake_alert_endpoint(location: str):
    """Пример эндпоинта для Earthquake Alert."""
    result = earthquake_alert(location)
    return {"result": result}


@app.post("/api/csv-tool")
async def csv_tool_endpoint(file_path: str):
    """Пример эндпоинта для CSV Tool."""
    result = csv_tool(file_path)
    return {"result": result}
