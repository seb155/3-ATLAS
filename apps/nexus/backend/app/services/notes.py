"""
Notes service with CRUD, search, and backlinks functionality.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, text, or_
from ..models.note import Note, WikiLink
from ..schemas.note import NoteCreate, NoteUpdate, SearchResult, BacklinkInfo
from typing import List, Optional
from uuid import UUID
from datetime import datetime
import html2text
import re


class NotesService:
    """Service for managing notes."""

    @staticmethod
    def _extract_plain_text(html_content: str) -> str:
        """Convert HTML content to plain text for search indexing."""
        if not html_content:
            return ""
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = True
        h.ignore_emphasis = True
        return h.handle(html_content).strip()

    @staticmethod
    def _extract_wiki_links(content: str) -> List[str]:
        """Extract [[wiki-link]] patterns from content."""
        if not content:
            return []
        # Match [[link-text]] pattern
        pattern = r'\[\[([^\]]+)\]\]'
        return re.findall(pattern, content)

    @staticmethod
    def create_note(db: Session, note: NoteCreate, user_id: UUID) -> Note:
        """Create a new note."""
        content_plain = NotesService._extract_plain_text(note.content)

        db_note = Note(
            title=note.title,
            content=note.content or "",
            content_plain=content_plain,
            parent_id=note.parent_id,
            is_folder=note.is_folder,
            user_id=user_id
        )
        db.add(db_note)
        db.commit()
        db.refresh(db_note)

        # Process wiki links after note is created
        NotesService._update_wiki_links(db, db_note)

        return db_note

    @staticmethod
    def get_notes(
        db: Session,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
        parent_id: Optional[UUID] = None,
        include_deleted: bool = False
    ) -> List[Note]:
        """Get notes for a user, optionally filtered by parent."""
        query = db.query(Note).filter(Note.user_id == user_id)

        if not include_deleted:
            query = query.filter(Note.deleted_at.is_(None))

        if parent_id is not None:
            query = query.filter(Note.parent_id == parent_id)

        return query.order_by(Note.is_folder.desc(), Note.title).offset(skip).limit(limit).all()

    @staticmethod
    def get_root_notes(db: Session, user_id: UUID) -> List[Note]:
        """Get root-level notes (no parent)."""
        return db.query(Note).filter(
            Note.user_id == user_id,
            Note.parent_id.is_(None),
            Note.deleted_at.is_(None)
        ).order_by(Note.is_folder.desc(), Note.title).all()

    @staticmethod
    def get_note(db: Session, note_id: UUID, user_id: UUID) -> Note | None:
        """Get a single note by ID."""
        return db.query(Note).filter(
            Note.id == note_id,
            Note.user_id == user_id,
            Note.deleted_at.is_(None)
        ).first()

    @staticmethod
    def get_note_with_children(db: Session, note_id: UUID, user_id: UUID) -> dict | None:
        """Get a note with its immediate children."""
        note = NotesService.get_note(db, note_id, user_id)
        if not note:
            return None

        children = db.query(Note).filter(
            Note.parent_id == note_id,
            Note.user_id == user_id,
            Note.deleted_at.is_(None)
        ).order_by(Note.is_folder.desc(), Note.title).all()

        return {
            "note": note,
            "children": children
        }

    @staticmethod
    def update_note(
        db: Session,
        note_id: UUID,
        user_id: UUID,
        note_update: NoteUpdate
    ) -> Note | None:
        """Update an existing note."""
        db_note = NotesService.get_note(db, note_id, user_id)
        if not db_note:
            return None

        update_data = note_update.model_dump(exclude_unset=True)

        # Update plain text if content changed
        if "content" in update_data:
            update_data["content_plain"] = NotesService._extract_plain_text(update_data["content"])

        for field, value in update_data.items():
            setattr(db_note, field, value)

        db.commit()
        db.refresh(db_note)

        # Update wiki links if content changed
        if "content" in update_data:
            NotesService._update_wiki_links(db, db_note)

        return db_note

    @staticmethod
    def delete_note(db: Session, note_id: UUID, user_id: UUID, hard_delete: bool = False) -> bool:
        """Delete a note (soft delete by default)."""
        db_note = NotesService.get_note(db, note_id, user_id)
        if not db_note:
            return False

        if hard_delete:
            db.delete(db_note)
        else:
            db_note.deleted_at = datetime.utcnow()

        db.commit()
        return True

    @staticmethod
    def search_notes(
        db: Session,
        user_id: UUID,
        query: str,
        limit: int = 20
    ) -> List[SearchResult]:
        """Full-text search across notes using PostgreSQL TSVECTOR."""
        if not query or len(query.strip()) < 2:
            return []

        # Use PostgreSQL full-text search
        search_query = func.plainto_tsquery('english', query)

        results = db.query(
            Note.id,
            Note.title,
            Note.content_plain,
            Note.is_folder,
            func.ts_rank(Note.content_tsvector, search_query).label('score')
        ).filter(
            Note.user_id == user_id,
            Note.deleted_at.is_(None),
            Note.content_tsvector.op('@@')(search_query)
        ).order_by(
            text('score DESC')
        ).limit(limit).all()

        search_results = []
        for r in results:
            # Create snippet from content_plain
            snippet = ""
            if r.content_plain:
                # Find the query terms and extract surrounding text
                lower_content = r.content_plain.lower()
                lower_query = query.lower()
                pos = lower_content.find(lower_query)
                if pos >= 0:
                    start = max(0, pos - 50)
                    end = min(len(r.content_plain), pos + len(query) + 100)
                    snippet = r.content_plain[start:end]
                    if start > 0:
                        snippet = "..." + snippet
                    if end < len(r.content_plain):
                        snippet = snippet + "..."
                else:
                    snippet = r.content_plain[:150] + "..." if len(r.content_plain) > 150 else r.content_plain

            search_results.append(SearchResult(
                id=r.id,
                title=r.title,
                snippet=snippet,
                score=float(r.score) if r.score else 0.0,
                is_folder=r.is_folder
            ))

        return search_results

    @staticmethod
    def get_backlinks(db: Session, note_id: UUID, user_id: UUID) -> List[BacklinkInfo]:
        """Get all notes that link to the specified note."""
        backlinks = db.query(
            Note.id,
            Note.title,
            WikiLink.link_text,
            WikiLink.created_at
        ).join(
            WikiLink, WikiLink.source_note_id == Note.id
        ).filter(
            WikiLink.target_note_id == note_id,
            Note.user_id == user_id,
            Note.deleted_at.is_(None)
        ).all()

        return [
            BacklinkInfo(
                id=b.id,
                title=b.title,
                link_text=b.link_text,
                created_at=b.created_at
            )
            for b in backlinks
        ]

    @staticmethod
    def _update_wiki_links(db: Session, note: Note) -> None:
        """Update wiki links for a note based on its content."""
        # Delete existing outgoing links
        db.query(WikiLink).filter(WikiLink.source_note_id == note.id).delete()

        # Extract and create new links
        link_texts = NotesService._extract_wiki_links(note.content)

        for link_text in link_texts:
            # Try to find target note by title (case-insensitive)
            target = db.query(Note).filter(
                Note.user_id == note.user_id,
                func.lower(Note.title) == link_text.lower(),
                Note.deleted_at.is_(None)
            ).first()

            if target and target.id != note.id:
                wiki_link = WikiLink(
                    source_note_id=note.id,
                    target_note_id=target.id,
                    link_text=link_text
                )
                db.add(wiki_link)

        db.commit()

    @staticmethod
    def get_note_tree(db: Session, user_id: UUID) -> List[dict]:
        """Get the complete note tree structure for a user."""
        notes = db.query(
            Note.id,
            Note.title,
            Note.parent_id,
            Note.is_folder
        ).filter(
            Note.user_id == user_id,
            Note.deleted_at.is_(None)
        ).order_by(Note.is_folder.desc(), Note.title).all()

        # Count children for each note
        children_counts = {}
        for n in notes:
            if n.parent_id:
                children_counts[n.parent_id] = children_counts.get(n.parent_id, 0) + 1

        return [
            {
                "id": n.id,
                "title": n.title,
                "parent_id": n.parent_id,
                "is_folder": n.is_folder,
                "children_count": children_counts.get(n.id, 0)
            }
            for n in notes
        ]

    @staticmethod
    def find_note_by_title(db: Session, user_id: UUID, title: str) -> Note | None:
        """Find a note by its exact title."""
        return db.query(Note).filter(
            Note.user_id == user_id,
            Note.title == title,
            Note.deleted_at.is_(None)
        ).first()

    @staticmethod
    def move_note(db: Session, note_id: UUID, user_id: UUID, new_parent_id: Optional[UUID]) -> Note | None:
        """Move a note to a new parent (or to root if new_parent_id is None)."""
        note = NotesService.get_note(db, note_id, user_id)
        if not note:
            return None

        # Validate new parent exists and belongs to user
        if new_parent_id:
            new_parent = NotesService.get_note(db, new_parent_id, user_id)
            if not new_parent:
                return None
            # Prevent moving a note into itself or its descendants
            if NotesService._is_descendant(db, new_parent_id, note_id):
                return None

        note.parent_id = new_parent_id
        db.commit()
        db.refresh(note)
        return note

    @staticmethod
    def _is_descendant(db: Session, potential_descendant_id: UUID, ancestor_id: UUID) -> bool:
        """Check if potential_descendant is a descendant of ancestor."""
        current = db.query(Note).filter(Note.id == potential_descendant_id).first()
        while current:
            if current.id == ancestor_id:
                return True
            if current.parent_id is None:
                return False
            current = db.query(Note).filter(Note.id == current.parent_id).first()
        return False
