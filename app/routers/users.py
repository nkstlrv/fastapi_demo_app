from typing import Annotated

from fastapi import APIRouter, status, Depends, Response, HTTPException
from config import schemas, models
from sqlalchemy.orm import Session
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


@router.get("/list", status_code=201)
def user_list(user: auth_dependency, db: db_dependency):
    users = db.query(models.User).all()
    return users


@router.get("/{id}", status_code=200)
def user_detail(user: auth_dependency, id: int, responce: Response, db: db_dependency):
    user = db.query(models.User).filter(models.User.id == id).first()
    if user:
        return user
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No user with such id"
        )


@router.get("/notes/{id}", status_code=200)
def user_notes(user: auth_dependency, id: int, responce: Response, db: db_dependency):
    user = db.query(models.User).filter(models.User.id == id).first()
    if user:
        notes = db.query(models.Note).filter(models.Note.user_id == id)
        return notes.all()
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No user with such id"
        )


@router.put("/update/email/{id}", status_code=status.HTTP_202_ACCEPTED)
def user_update_email(
    user: auth_dependency, id: int, request: schemas.UserUpdateEmail, db: db_dependency
):
    user = db.query(models.User).filter(models.User.id == id)

    if not user.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No user with such id"
        )

    user.update({"email": request.email})
    db.commit()
    return {"message": "User's email updated successfully", "user": user.first()}


@router.put(
    "/update/username/{id}",
    status_code=status.HTTP_202_ACCEPTED,
)
def user_update_username(
    user: auth_dependency,
    id: int,
    request: schemas.UserUpdateUsername,
    db: db_dependency,
):
    user = db.query(models.User).filter(models.User.id == id)

    if not user.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No user with such id"
        )

    user.update({"username": request.username})
    db.commit()
    return {"message": "User's username updated successfully", "user": user.first()}


@router.put(
    "/update/password/{id}",
    status_code=status.HTTP_202_ACCEPTED,
)
def user_update_password(
    user: auth_dependency,
    id: int,
    request: schemas.UserUpdatePassword,
    db: db_dependency,
):
    user = db.query(models.User).filter(models.User.id == id)

    if not user.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No user with such id"
        )

    # if pwd_cxt.hash(request.old_password) != user.first().password:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="Previous password is incorrect",
    #     )

    if request.password1 != request.password2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match",
        )

    user.update({"password": bcrypt_context.hash(request.password1)})
    db.commit()
    return {"message": "User's password updated successfully", "user": user.first()}


@router.delete("/delete/{id}", status_code=204)
def user_destroy(user: auth_dependency, id: int, db: db_dependency):
    user_to_delete = db.query(models.User).filter(models.User.id == id)

    if not user_to_delete.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No user with such id"
        )

    user_to_delete.delete(synchronize_session=False)
    db.commit()
    return {"message": "User successfully deleted"}
