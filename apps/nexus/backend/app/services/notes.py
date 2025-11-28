from sqlalchemy.orm import Session
from ..models.note import Note
from ..schemas.note import NoteCreate, NoteUpdate
from typing import List
import html2text


class NotesService:
    @staticmethod
    def create_note(db: Session, note: NoteCreate, user_id: int) -> Note:
        # Convert HTML to plain text for search
        h = html2text.HTML2Text()
        h.ignore_links = False
        content_plain = h.handle(note.content) if note.content else ""

        db_note = Note(
            **note.model_dump(),
            user_id=user_id,
            content_plain=content_plain
        )
        db.add(db_note)
        db.commit()
        db.refresh(db_note)
        return db_note

    @staticmethod
    def get_notes(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Note]:
        return db.query(Note).filter(
            Note.user_id == user_id,
            Note.deleted_at.is_(None)
        ).offset(skip).limit(limit).all()

    @staticmethod
    def get_note(db: Session, note_id: int, user_id: int) -> Note | None:
        return db.query(Note).filter(
            Note.id == note_id,
            Note.user_id == user_id,
            Note.deleted_at.is_(None)
        ).first()

    @staticmethod
    def update_note(db: Session, note_id: int, user_id: int, note_update: NoteUpdate) -> Note | None:
        db_note = NotesService.get_note(db, note_id, user_id)
        if not db_note:
            return None

        update_data = note_update.model_dump(exclude_unset=True)

        # Update plain text if content changed
        if "content" in update_data:
            h = html2text.HTML2Text()
            update_data["content_plain"] = h.handle(update_data["content"])

        for field, value in update_data.items():
            setattr(db_note, field, value)

        db.commit()
        db.refresh(db_note)
        return db_note

    @staticmethod
    def delete_note(db: Session, note_id: int, user_id: int) -> bool:
        db_note = NotesService.get_note(db, note_id, user_id)
        if not db_note:
            return False

        # Soft delete
        from datetime import datetime
        db_note.deleted_at = datetime.utcnow()
        db.commit()
        return True
