from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..schemas.note import Note, NoteCreate, NoteUpdate
from ..services.notes import NotesService
from ..utils.dependencies import get_current_user
from ..models.user import User

router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("", response_model=Note, status_code=status.HTTP_201_CREATED)
def create_note(
    note: NoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return NotesService.create_note(db, note, current_user.id)


@router.get("", response_model=List[Note])
def get_notes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return NotesService.get_notes(db, current_user.id, skip, limit)


@router.get("/{note_id}", response_model=Note)
def get_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    note = NotesService.get_note(db, note_id, current_user.id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.put("/{note_id}", response_model=Note)
def update_note(
    note_id: int,
    note_update: NoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    note = NotesService.update_note(db, note_id, current_user.id, note_update)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not NotesService.delete_note(db, note_id, current_user.id):
        raise HTTPException(status_code=404, detail="Note not found")
