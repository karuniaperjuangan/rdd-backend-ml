from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from dotenv import load_dotenv
import os
from routers.predict import router as predict_router

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predict_router)

@app.get("/")

@app.get("/api")
async def root():
    return {"message": "Hello World"}

import uvicorn
if __name__ == "__main__":
    uvicorn.run(app,port=2045)