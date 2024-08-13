from fastapi import FastAPI
import uvicorn
import argparse
import json
from utils.configure.configure import Configure

app = FastAPI()


from apis.v1.authenticate.authenticate import *


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dev",
        "-D",
        action="store_true",
        help="Run in development mode",
    )
    args = parser.parse_args()

    config = json.load(open("config.json"))
    devConfig = json.load(open("config.development.json"))

    config = Configure("config.json")
    config.Load()

    if args.dev:
        overiddenConfig = Configure("config.development.json")
        overiddenConfig.Load()
        config.OverridenBy(overiddenConfig)

    uvicorn.run(
        app="main:app",
        host=config.Get("host", "localhost"),
        port=config.Get("port", 8080),
        reload=args.dev,
    )
