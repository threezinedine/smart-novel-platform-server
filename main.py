from fastapi import FastAPI
import uvicorn
import argparse
import json

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


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

    host = devConfig["host"] if args.dev else config["host"]
    port = devConfig["port"] if args.dev else config["port"]

    uvicorn.run(
        app="main:app",
        host=host,
        port=port,
        reload=args.dev,
    )
