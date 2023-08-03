from fastapi import APIRouter, status, Depends, Response, HTTPException
from config import schemas, models
from sqlalchemy.orm import Session
from config.database import get_db
from config.hashing import pwd_cxt


router = APIRouter()


@router.post("/auth/user/create", tags=["users"])
def user_create(request: schemas.User, db: Session = Depends(get_db)):
    hashed_password = pwd_cxt.hash(request.password)

    new_user = models.User(
        username=request.username, email=request.email, password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User created successfully", "user": new_user}


@router.get("/auth/user/list", status_code=201, tags=["users"])
def user_list(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users


@router.get("/auth/user/{id}", status_code=200, tags=["users"])
def user_detail(id: int, responce: Response, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if user:
        return user
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No user with such id"
        )


@router.get("/auth/user/notes/{id}", status_code=200, tags=["users"])
def user_notes(id: int, responce: Response, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if user:
        notes = db.query(models.Note).filter(models.Note.user_id == id)
        return notes.all()
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No user with such id"
        )


@router.put(
    "/auth/user/update/email/{id}", status_code=status.HTTP_202_ACCEPTED, tags=["users"]
)
def user_update_email(
    id: int, request: schemas.UserUpdateEmail, db: Session = Depends(get_db)
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
    "/auth/user/update/username/{id}",
    status_code=status.HTTP_202_ACCEPTED,
    tags=["users"],
)
def user_update_username(
    id: int, request: schemas.UserUpdateUsername, db: Session = Depends(get_db)
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
    "/auth/user/update/password/{id}",
    status_code=status.HTTP_202_ACCEPTED,
    tags=["users"],
)
def user_update_password(
    id: int, request: schemas.UserUpdatePassword, db: Session = Depends(get_db)
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

    user.update({"password": pwd_cxt.hash(request.password1)})
    db.commit()
    return {"message": "User's password updated successfully", "user": user.first()}


@router.delete("/auth/user/delete/{id}", status_code=204, tags=["users"])
def user_destroy(id: int, db: Session = Depends(get_db)):
    user_to_delete = db.query(models.User).filter(models.User.id == id)

    if not user_to_delete.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No user with such id"
        )

    user_to_delete.delete(synchronize_session=False)
    db.commit()
    return {"message": "User successfully deleted"}
