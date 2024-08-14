from fastapi import FastAPI
import uvicorn
import argparse
import json
from utils.configure.configure import Configure
import apis.v1.users.users as auth
from fastapi import Depends
from config import initialize_config, config

parser = argparse.ArgumentParser()
parser.add_argument(
    "--dev",
    "-D",
    action="store_true",
    help="Run in development mode",
)
args = parser.parse_args()

app = FastAPI()

app.include_router(auth.router)

if __name__ == "__main__":
    initialize_config(args.dev)

    uvicorn.run(
        app="main:app",
        host=config.Get("host", "localhost"),
        port=config.Get("port", 8080),
        reload=args.dev,
    )
