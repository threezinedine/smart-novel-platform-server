import argparse
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
import apis.v1.users.users as auth
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.Get("allow_origins", []),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)

if __name__ == "__main__":

    uvicorn.run(
        app="main:app",
        host=config.Get("host", "localhost"),
        port=config.Get("port", 8080),
        reload=args.dev,
    )
