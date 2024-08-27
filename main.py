import argparse

from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from config import initialize_config, config

parser = argparse.ArgumentParser()
parser.add_argument(
    "--dev",
    "-D",
    action="store_true",
    help="Run in development mode",
)
args = parser.parse_args()
initialize_config(args.dev)

from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
# app.mount("/", StaticFiles(directory="publics"), name="static")
# app.mount("/static", StaticFiles(directory="publics/statics"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.Get("allow_origins", []),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# @app.get("/")
# def root():
#     try:
#         with open("publics/index.html") as f:
#             return HTMLResponse(content=f.read(), status_code=200)
#     except FileNotFoundError:
#         return {"error": "file not found"}


# app.mount("/static", StaticFiles(directory="publics"), name="static")

import apis.v1.users.users as auth

app.include_router(auth.router)


if __name__ == "__main__":
    uvicorn.run(
        app="main:app",
        host=config.Get("host", "localhost"),
        port=config.Get("port", 8080),
        reload=args.dev,
    )
