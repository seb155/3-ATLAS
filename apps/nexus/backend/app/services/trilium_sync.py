"""
TriliumSyncService - Bidirectional synchronization with TriliumNext via ETAPI.

Features:
- Import notes from Trilium to NEXUS
- Push changes from NEXUS to Trilium
- Detect and handle conflicts
- Preserve Trilium hierarchy
"""

import aiohttp
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from uuid import UUID
import logging
import html2text

from ..config import get_settings
from ..models.note import Note
from ..models.trilium_sync import TriliumSync

logger = logging.getLogger(__name__)


class TriliumAPIError(Exception):
    """Custom exception for Trilium API errors."""
    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message
        super().__init__(f"Trilium API Error ({status}): {message}")


class TriliumSyncService:
    """
    Service for syncing notes between NEXUS and TriliumNext.

    Usage:
        service = TriliumSyncService()
        async with service:
            notes = await service.get_note("abc123")
    """

    def __init__(self, etapi_url: Optional[str] = None, etapi_token: Optional[str] = None):
        settings = get_settings()
        self.base_url = (etapi_url or settings.trilium_etapi_url or "").rstrip("/")
        self.token = etapi_token or settings.trilium_etapi_token
        self._session: Optional[aiohttp.ClientSession] = None
        self._h2t = html2text.HTML2Text()
        self._h2t.ignore_links = False
        self._h2t.ignore_images = True

    async def __aenter__(self):
        """Create HTTP session on context entry."""
        self._session = aiohttp.ClientSession(
            headers={"Authorization": self.token}
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close HTTP session on context exit."""
        if self._session:
            await self._session.close()
            self._session = None

    @property
    def is_configured(self) -> bool:
        """Check if Trilium integration is configured."""
        return bool(self.base_url and self.token)

    # =========================================================================
    # ETAPI Methods
    # =========================================================================

    async def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Make an authenticated request to Trilium ETAPI."""
        if not self._session:
            raise RuntimeError("TriliumSyncService must be used as async context manager")

        url = f"{self.base_url}/etapi{endpoint}"

        async with self._session.request(method, url, **kwargs) as response:
            if response.status == 401:
                raise TriliumAPIError(401, "Not authenticated - check ETAPI token")
            if response.status == 404:
                raise TriliumAPIError(404, f"Note not found: {endpoint}")
            if response.status >= 400:
                text = await response.text()
                raise TriliumAPIError(response.status, text)

            if response.content_type == "application/json":
                return await response.json()
            return {"content": await response.text()}

    async def get_app_info(self) -> Dict[str, Any]:
        """Get Trilium app information (useful for testing connection)."""
        return await self._request("GET", "/app-info")

    async def get_note(self, note_id: str) -> Dict[str, Any]:
        """Get a note by ID from Trilium."""
        return await self._request("GET", f"/notes/{note_id}")

    async def get_note_content(self, note_id: str) -> str:
        """Get the content of a note."""
        result = await self._request("GET", f"/notes/{note_id}/content")
        return result.get("content", "")

    async def search_notes(
        self,
        search: str = "*",
        limit: int = 100,
        fast_search: bool = True
    ) -> List[Dict[str, Any]]:
        """Search notes in Trilium."""
        params = {
            "search": search,
            "limit": limit,
            "fastSearch": str(fast_search).lower()
        }
        result = await self._request("GET", "/notes", params=params)
        return result.get("results", [])

    async def create_note(
        self,
        parent_note_id: str,
        title: str,
        content: str = "",
        note_type: str = "text",
        mime: str = "text/html"
    ) -> Dict[str, Any]:
        """Create a new note in Trilium."""
        data = {
            "parentNoteId": parent_note_id,
            "title": title,
            "type": note_type,
            "mime": mime,
            "content": content
        }
        return await self._request("POST", "/create-note", json=data)

    async def update_note(self, note_id: str, title: Optional[str] = None) -> Dict[str, Any]:
        """Update note metadata in Trilium."""
        data = {}
        if title is not None:
            data["title"] = title
        return await self._request("PATCH", f"/notes/{note_id}", json=data)

    async def update_note_content(self, note_id: str, content: str) -> None:
        """Update note content in Trilium."""
        await self._request(
            "PUT",
            f"/notes/{note_id}/content",
            data=content,
            headers={"Content-Type": "text/html"}
        )

    async def delete_note(self, note_id: str) -> None:
        """Delete a note in Trilium."""
        await self._request("DELETE", f"/notes/{note_id}")

    # =========================================================================
    # Sync Methods
    # =========================================================================

    async def import_from_trilium(
        self,
        db: Session,
        user_id: UUID,
        trilium_note_id: str = "root",
        parent_nexus_id: Optional[UUID] = None,
        recursive: bool = True
    ) -> Dict[str, Any]:
        """
        Import notes from Trilium into NEXUS.

        Args:
            db: Database session
            user_id: NEXUS user ID
            trilium_note_id: Starting Trilium note ID (default: root)
            parent_nexus_id: Parent note ID in NEXUS (None for root)
            recursive: Whether to import child notes recursively

        Returns:
            Dict with import statistics
        """
        stats = {"imported": 0, "skipped": 0, "errors": 0}

        # Skip system notes
        if trilium_note_id.startswith("_"):
            return stats

        try:
            trilium_note = await self.get_note(trilium_note_id)
        except TriliumAPIError as e:
            logger.error(f"Failed to get Trilium note {trilium_note_id}: {e}")
            stats["errors"] += 1
            return stats

        # Skip protected notes
        if trilium_note.get("isProtected"):
            logger.info(f"Skipping protected note: {trilium_note.get('title')}")
            stats["skipped"] += 1
            return stats

        # Check if already synced
        existing = db.query(TriliumSync).filter(
            TriliumSync.trilium_note_id == trilium_note_id
        ).first()

        if existing:
            # Note already exists - check for updates
            stats["skipped"] += 1
        else:
            # Import new note
            content = ""
            if trilium_note.get("type") == "text":
                try:
                    content = await self.get_note_content(trilium_note_id)
                except TriliumAPIError:
                    content = ""

            # Create NEXUS note
            nexus_note = Note(
                title=trilium_note.get("title", "Untitled"),
                content=content,
                content_plain=self._h2t.handle(content).strip() if content else "",
                parent_id=parent_nexus_id,
                is_folder=len(trilium_note.get("childNoteIds", [])) > 0,
                user_id=user_id
            )
            db.add(nexus_note)
            db.flush()  # Get the ID

            # Create sync mapping
            sync_entry = TriliumSync(
                nexus_note_id=nexus_note.id,
                trilium_note_id=trilium_note_id,
                trilium_utc_modified=self._parse_trilium_date(
                    trilium_note.get("utcDateModified")
                ),
                sync_status="synced",
                source="trilium",
                trilium_type=trilium_note.get("type"),
                trilium_mime=trilium_note.get("mime")
            )
            db.add(sync_entry)
            stats["imported"] += 1

            # Import children recursively
            if recursive:
                for child_id in trilium_note.get("childNoteIds", []):
                    child_stats = await self.import_from_trilium(
                        db, user_id, child_id, nexus_note.id, recursive=True
                    )
                    stats["imported"] += child_stats["imported"]
                    stats["skipped"] += child_stats["skipped"]
                    stats["errors"] += child_stats["errors"]

        db.commit()
        return stats

    async def push_to_trilium(
        self,
        db: Session,
        nexus_note_id: UUID,
        parent_trilium_id: str = "root"
    ) -> Optional[str]:
        """
        Push a NEXUS note to Trilium.

        Returns:
            Trilium note ID if successful, None otherwise
        """
        nexus_note = db.query(Note).filter(Note.id == nexus_note_id).first()
        if not nexus_note:
            return None

        # Check if already synced
        sync_entry = db.query(TriliumSync).filter(
            TriliumSync.nexus_note_id == nexus_note_id
        ).first()

        if sync_entry:
            # Update existing Trilium note
            await self.update_note(sync_entry.trilium_note_id, title=nexus_note.title)
            await self.update_note_content(sync_entry.trilium_note_id, nexus_note.content or "")

            # Update sync status
            sync_entry.last_synced_at = datetime.utcnow()
            sync_entry.sync_status = "synced"
            db.commit()

            return sync_entry.trilium_note_id
        else:
            # Create new note in Trilium
            result = await self.create_note(
                parent_note_id=parent_trilium_id,
                title=nexus_note.title,
                content=nexus_note.content or "",
                note_type="text",
                mime="text/html"
            )

            trilium_note_id = result.get("note", {}).get("noteId")
            if trilium_note_id:
                # Create sync mapping
                sync_entry = TriliumSync(
                    nexus_note_id=nexus_note_id,
                    trilium_note_id=trilium_note_id,
                    sync_status="synced",
                    source="nexus"
                )
                db.add(sync_entry)
                db.commit()

            return trilium_note_id

    async def sync_all(self, db: Session, user_id: UUID) -> Dict[str, int]:
        """
        Perform full bidirectional sync.

        Returns:
            Dict with sync statistics
        """
        stats = {
            "pulled": 0,
            "pushed": 0,
            "conflicts": 0,
            "errors": 0
        }

        # 1. Pull changes from Trilium
        pull_stats = await self.import_from_trilium(db, user_id)
        stats["pulled"] = pull_stats["imported"]
        stats["errors"] += pull_stats["errors"]

        # 2. Push pending changes to Trilium
        pending = db.query(TriliumSync).filter(
            TriliumSync.sync_status == "pending_push"
        ).all()

        for sync_entry in pending:
            try:
                await self.push_to_trilium(db, sync_entry.nexus_note_id)
                stats["pushed"] += 1
            except TriliumAPIError as e:
                logger.error(f"Failed to push note: {e}")
                stats["errors"] += 1

        return stats

    def _parse_trilium_date(self, date_str: Optional[str]) -> Optional[int]:
        """Parse Trilium date string to milliseconds timestamp."""
        if not date_str:
            return None
        try:
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            return int(dt.timestamp() * 1000)
        except (ValueError, TypeError):
            return None

    # =========================================================================
    # Query Methods
    # =========================================================================

    def get_sync_status(self, db: Session, nexus_note_id: UUID) -> Optional[TriliumSync]:
        """Get sync status for a NEXUS note."""
        return db.query(TriliumSync).filter(
            TriliumSync.nexus_note_id == nexus_note_id
        ).first()

    def get_pending_syncs(self, db: Session) -> List[TriliumSync]:
        """Get all notes pending sync."""
        return db.query(TriliumSync).filter(
            TriliumSync.sync_status.in_(["pending_push", "pending_pull"])
        ).all()

    def mark_for_sync(self, db: Session, nexus_note_id: UUID) -> None:
        """Mark a note as needing to be pushed to Trilium."""
        sync_entry = self.get_sync_status(db, nexus_note_id)
        if sync_entry:
            sync_entry.sync_status = "pending_push"
            db.commit()
