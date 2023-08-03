from typing import Annotated
from fastapi import APIRouter, status, Depends, HTTPException
from config import schemas, models
from config.database import get_db
from config.hashing import bcrypt_context
from routers.authentication import get_current_user

auth_dependency = Annotated[dict, Depends(get_current_user)]
db_dependency = Annotated[dict, Depends(get_db)]

router = APIRouter(tags=["Users"], prefix="/auth/user")


@router.post("/create")
def user_create(request: schemas.User, db: db_dependency):
    hashed_password = bcrypt_context.hash(request.password)

    new_user = models.User(
        username=request.username, email=request.email, password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User created successfully", "user": new_user}


@router.put("/update/email/", status_code=status.HTTP_202_ACCEPTED)
def user_update_email(
    user: auth_dependency, request: schemas.UserUpdateEmail, db: db_dependency
):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    user_to_update = db.query(models.User).filter(models.User.id == user.get("id"))

    if not user_to_update.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    user_to_update.update({"email": request.email})
    db.commit()
    return {
        "message": "Email successfully updated",
        "user": user_to_update.first(),
    }


@router.put("/update/username/", status_code=status.HTTP_202_ACCEPTED)
def user_update_username(
    user: auth_dependency, request: schemas.UserUpdateUsername, db: db_dependency
):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    user_to_update = db.query(models.User).filter(models.User.id == user.get("id"))

    if not user_to_update.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    user_to_update.update({"username": request.username})
    db.commit()
    return {
        "message": "Username successfully updated",
        "user": user_to_update.first(),
    }


@router.put("/update/password/", status_code=status.HTTP_202_ACCEPTED)
def user_update_password(
    user: auth_dependency, request: schemas.UserUpdatePassword, db: db_dependency
):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    user_to_update = db.query(models.User).filter(models.User.id == user.get("id"))

    if not user_to_update.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    if request.password1 != request.password2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match"
        )

    user_to_update.update({"password": bcrypt_context.hash(request.password1)})
    db.commit()
    return {
        "message": "Password successfully updated",
        "user": user_to_update.first(),
    }


@router.delete("/delete/", status_code=204)
def user_destroy(user: auth_dependency, db: db_dependency):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    user_to_delete = db.query(models.User).filter(models.User.id == user.get("id"))

    if not user_to_delete.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    user_to_delete.delete(synchronize_session=False)
    db.commit()
    return {"message": "User successfully deleted"}
