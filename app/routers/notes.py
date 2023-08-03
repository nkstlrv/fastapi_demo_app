from fastapi import APIRouter, status, Depends, Response, HTTPException
from config import schemas, models
from datetime import datetime
from config.database import get_db
from .authentication import get_current_user
from typing import Annotated


router = APIRouter(tags=["Notes"], prefix="/note")

auth_dependency = Annotated[dict, Depends(get_current_user)]
db_dependency = Annotated[dict, Depends(get_db)]


@router.post("/create", status_code=status.HTTP_201_CREATED)
def note_create(user: auth_dependency, request: schemas.Note, db: db_dependency):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )
    new_note = models.Note(
        title=request.title, body=request.body, user_id=user.get("id")
    )
    db.add(new_note)
    db.commit()
    db.refresh(new_note)

    return new_note


@router.get("/list")
def note_list(user: auth_dependency, db: db_dependency):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )
    all_notes = (
        db.query(models.Note).filter(models.Note.user_id == user.get("id")).all()
    )
    return {"notes": all_notes}


@router.get("/{id}", status_code=200)
def note_details(user: auth_dependency, id: int, responce: Response, db: db_dependency):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )
    note = db.query(models.Note).filter(models.Note.id == id).first()

    if not note:
        responce.status_code = status.HTTP_404_NOT_FOUND
        raise HTTPException(status_code=404, detail="No note with such id")

    if note.user_id != user.get("id"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    return note


@router.delete("/delete/{id}", status_code=status.HTTP_204_NO_CONTENT)
def note_destroy(user: auth_dependency, id: int, responce: Response, db: db_dependency):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )
    note = db.query(models.Note).filter(models.Note.id == id).first()

    if not note:
        responce.status_code = status.HTTP_404_NOT_FOUND
        raise HTTPException(status_code=404, detail="Not found")

    if note.user_id != user.get("id"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    db.query(models.Note).filter(models.Note.id == id).delete(synchronize_session=False)
    db.commit()
    return {"message": "Deleted"}


@router.put("/update/{id}", status_code=status.HTTP_202_ACCEPTED)
def note_update(
    user: auth_dependency, id: int, request: schemas.Note, db: db_dependency
):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    note = db.query(models.Note).filter(models.Note.id == id)

    if not note.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    if note.first().user_id != user.get("id"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

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
