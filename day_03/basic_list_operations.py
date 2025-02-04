from fastapi import FastAPI, HTTPException
import uvicorn
import os
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

data_list: list[str] = []

MAX_LIST_SIZE = 100


@app.post("/add")
def add_item(item: str):
    if len(data_list) >= MAX_LIST_SIZE:
        raise HTTPException(
            status_code=400, detail="List is full. Cannot add more items."
        )
    data_list.append(item)
    return {"message": f"Item {json.dumps(item)} added successfully."}


@app.delete("/remove")
def remove_item(item: str):
    if item not in data_list:
        raise HTTPException(status_code=404, detail=f"Item {item!r} not found.")
    data_list.remove(item)
    return {"message": f"Item {json.dumps(item)} removed successfully."}


@app.get("/")
def read_root():
    return {"message": "Welcome to the basic_list_operations API!"}


@app.get("/search")
def search_item(item: str):
    if item not in data_list:
        return {"index": -1}
    return {"index": data_list.index(item)}


@app.get("/sort")
def sort_list():
    data_list.sort()
    return {"sorted_list": data_list}


@app.get("/length")
def get_length():
    return {"length": len(data_list)}


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    uvicorn.run(app, host="0.0.0.0", port=port)
