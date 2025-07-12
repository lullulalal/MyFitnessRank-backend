# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import running_route
from .core.db import init_db
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup code here
    init_db()
    yield
    # shutdown code here (optional)

app = FastAPI(root_path="/myfitnessrank", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://lullulalal.github.io",
    ],
    allow_origin_regex=r"http://localhost:\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello from MyFitnessRank backend!"}

app.include_router(running_route.router)