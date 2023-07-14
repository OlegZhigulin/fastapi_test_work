from fastapi import FastAPI

from src.routers import api_router_v1
from src.dependences import create_db


app = FastAPI(
    title='Тестовое задание',
    description='Микросервис для работы с запиисями в бд'
)

app.include_router(api_router_v1)


@app.on_event('startup')
async def startup_db():
    await create_db()
