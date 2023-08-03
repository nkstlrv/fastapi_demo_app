import uvicorn
from fastapi import FastAPI, Depends, status, Response, HTTPException
from notes import models, schemas
from sqlalchemy.orm import Session
from datetime import datetime
from notes.hashing import pwd_cxt

models.Base.metadata.create_all(bind=models.engine)


def get_db():
    db = models.MySession()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()


@app.get("/")
def index():
    return {"message": "Hello, there!"}


@app.post("/note/create", status_code=status.HTTP_201_CREATED, tags=["notes"])
def note_create(request: schemas.Note, db: Session = Depends(get_db)):
    new_note = models.Note(title=request.title, body=request.body)
    db.add(new_note)
    db.commit()
    db.refresh(new_note)

    return new_note


@app.get("/note/list", tags=["notes"])
def note_list(db: Session = Depends(get_db)):
    all_notes = db.query(models.Note).all()
    return all_notes


@app.get("/note/{id}", status_code=200, tags=["notes"])
def note_details(id: int, responce: Response, db: Session = Depends(get_db)):
    note = db.query(models.Note).filter(models.Note.id == id).first()

    if not note:
        responce.status_code = status.HTTP_404_NOT_FOUND
        raise HTTPException(status_code=404, detail="No note with such id")
    return note


@app.delete("/note/delete/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["notes"])
def note_destroy(id: int, responce: Response, db: Session = Depends(get_db)):
    note = db.query(models.Note).filter(models.Note.id == id).first()

    if note:
        db.query(models.Note).filter(models.Note.id == id).delete(
            synchronize_session=False
        )
        db.commit()
        return {"message": "Deleted"}
    else:
        responce.status_code = status.HTTP_404_NOT_FOUND
        raise HTTPException(status_code=404, detail="No note with such id")


@app.put("/note/update/{id}", status_code=status.HTTP_202_ACCEPTED, tags=["notes"])
def note_update(id: int, request: schemas.Note, db: Session = Depends(get_db)):
    note = db.query(models.Note).filter(models.Note.id == id)

    if not note.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No note with such id"
        )

    else:
        note.update(
            {
                "title": request.title,
                "body": request.body,
                "edited_at": datetime.utcnow(),
            }
        )
        db.commit()
        return {"message": "Updated successfully", "note": note.first()}


@app.post("/auth/user/create", tags=["users"])
def user_create(request: schemas.User, db: Session = Depends(get_db)):
    hashed_password = pwd_cxt.hash(request.password)

    new_user = models.User(
        username=request.username, email=request.email, password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User created successfully", "user": new_user}


@app.get("/auth/user/list", status_code=201, tags=["users"])
def user_list(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users


@app.get("/auth/user/{id}", status_code=200, tags=["users"])
def user_detail(id: int, responce: Response, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if user:
        return user
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No user with such id"
        )


@app.put(
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


@app.put(
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


@app.put(
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


@app.delete("/auth/user/delete/{id}", status_code=204, tags=["users"])
def user_destroy(id: int, db: Session = Depends(get_db)):
    user_to_delete = db.query(models.User).filter(models.User.id == id)

    if not user_to_delete.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No user with such id"
        )

    user_to_delete.delete(synchronize_session=False)
    db.commit()
    return {"message": "User successfully deleted"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
