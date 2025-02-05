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
    logger.info(f"Attempting to add item: {item}")
    if len(data_list) >= MAX_LIST_SIZE:
        logger.error(f"Cannot add item {item}. List is full.")
        raise HTTPException(
            status_code=400, detail="List is full. Cannot add more items."
        )
    data_list.append(item)
    logger.info(f"Item {item} added successfully. Current list size: {len(data_list)}")
    return {"message": f"Item {json.dumps(item)} added successfully."}


@app.delete("/remove")
def remove_item(item: str):
    logger.info(f"Attempting to remove item: {item}")
    if item not in data_list:
        logger.error(f"Item {item} not found in the list.")
        raise HTTPException(status_code=404, detail=f"Item {item!r} not found.")
    data_list.remove(item)
    logger.info(
        f"Item {item} removed successfully. Current list size: {len(data_list)}"
    )
    return {"message": f"Item {json.dumps(item)} removed successfully."}


@app.get("/")
def read_root():
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to the basic_list_operations API!"}


@app.get("/search")
def search_item(item: str):
    logger.info(f"Attempting to search for item: {item}")
    if item not in data_list:
        logger.info(f"Item {item} not found in the list.")
        return {"index": -1}
    index = data_list.index(item)
    logger.info(f"Item {item} found at index {index}.")
    return {"index": index}


@app.get("/sort")
def sort_list():
    logger.info("Attempting to sort the list.")
    data_list.sort()
    logger.info(f"List sorted successfully. Current list: {data_list}")
    return {"sorted_list": data_list}


@app.get("/length")
def get_length():
    logger.info("Fetching the length of the list.")
    length = len(data_list)
    logger.info(f"Current list length: {length}")
    return {"length": length}


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    uvicorn.run(app, host="0.0.0.0", port=port)
