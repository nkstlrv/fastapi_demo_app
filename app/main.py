from typing import Annotated

import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from routers import users, notes, authentication
from config.database import Base, engine, get_db
from routers.authentication import get_current_user

auth_dependency = Annotated[dict, Depends(get_current_user)]
db_dependency = Annotated[dict, Depends(get_db)]

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(notes.router)
app.include_router(users.router)
app.include_router(authentication.router)


@app.get("/")
def index(user: auth_dependency, db: db_dependency):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )
    return {"user": user}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
