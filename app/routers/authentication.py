from datetime import timedelta
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from config import schemas, models, hashing
from config.database import get_db
from config.jwt_token import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token

router = APIRouter(tags=["Authentication"], prefix="/auth")


@router.post("/login")
def login(request: schemas.LoginSchema, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == request.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No user with this credentials",
        )
    if not hashing.hash_object.verify(request.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}
