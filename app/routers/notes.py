from fastapi import APIRouter, status, Depends, Response, HTTPException
from config import schemas, models
from sqlalchemy.orm import Session
from datetime import datetime
from config.database import get_db
from .authentication import get_current_user
from typing import Annotated


router = APIRouter(tags=["Notes"], prefix="/note")

auth_dependency = Annotated[dict, Depends(get_current_user)]


@router.post("/create", status_code=status.HTTP_201_CREATED)
def note_create(request: schemas.Note, db: Session = Depends(get_db)):
    new_note = models.Note(title=request.title, body=request.body, user_id=1)
    db.add(new_note)
    db.commit()
    db.refresh(new_note)

    return new_note


@router.get("/list")
def note_list(user: auth_dependency, db: Session = Depends(get_db)):
    all_notes = db.query(models.Note).all()
    return all_notes


@router.get("/{id}", status_code=200)
def note_details(id: int, responce: Response, db: Session = Depends(get_db)):
    note = db.query(models.Note).filter(models.Note.id == id).first()

    if not note:
        responce.status_code = status.HTTP_404_NOT_FOUND
        raise HTTPException(status_code=404, detail="No note with such id")
    return note


@router.get("/by-user-id/{user_id}", status_code=200)
def note_details_by_user_id(
    user_id: int, responce: Response, db: Session = Depends(get_db)
):
    note = db.query(models.Note).filter(models.Note.user_id == user_id).first()

    if not note:
        responce.status_code = status.HTTP_404_NOT_FOUND
        raise HTTPException(status_code=404, detail="No note with such id")
    return note


@router.delete("/delete/{id}", status_code=status.HTTP_204_NO_CONTENT)
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


@router.put("/update/{id}", status_code=status.HTTP_202_ACCEPTED)
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
