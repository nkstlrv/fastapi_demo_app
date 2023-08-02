import uvicorn
from fastapi import FastAPI
from notes import models, schemas

models.Base.metadata.create_all(bind=models.engine)

app = FastAPI()


@app.get('/')
def index():
    return {'message': 'Hello, there!'}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
