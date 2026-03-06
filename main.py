import asyncio
from wialon_parser import get_objects, get_buffer
from fastapi import FastAPI, HTTPException
from typing import List
import logging


app = FastAPI()


logging.basicConfig(
    level=logging.INFO,  # минимальный уровень логов
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("main")
logger.info("Приложение запускается...")

@app.on_event("startup")
async def lifespan():
    asyncio.create_task(get_objects())

@app.get("/objects")
async def get_wialon_objects() -> List:
    return get_buffer()

@app.get("/objects/{id}")
async def get_wialon_objects(id: int) -> dict: 
    buffer = get_buffer()
    matches = [x for x in buffer if x["id"] == id]
    if len(matches) > 0:
        return matches[0]
    else:
        raise HTTPException(status_code=404, detail="Объект не найден")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

