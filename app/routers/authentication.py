from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from config import schemas, models
from config.database import get_db

router = APIRouter(tags=["Authentication"], prefix="auth/")


@router.post("/login")
def login(request: schemas.LoginSchema, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == request.username)
    if not user.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid credentials"
        )

    return {"message": "Login is successful", "user": user.first()}
