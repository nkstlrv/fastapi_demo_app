from fastapi import FastAPI


app = FastAPI()

@app.get('/')
def demo_endpoint():
    return {'message': 'Hello, FastAPI!'}