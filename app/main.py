import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.get('/')
def index():
    return {'message': 'Hello, there!'}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
