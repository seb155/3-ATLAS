from sqlalchemy.orm import Session

from app.models.auth import AuditLog
from app.services.logger import SystemLog


def log_audit(
    db: Session, user_id: str, action: str, target_type: str, target_id: str, details: dict = None
):
    """
    Creates an audit log entry.
    """
    try:
        log_entry = AuditLog(
            user_id=user_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            details=details or {},
        )
        db.add(log_entry)
        # We don't commit here to allow the caller to commit as part of a transaction.
        # But if we want to ensure logs are written even if main transaction fails?
        # Usually audit log should be part of the same transaction for integrity.
        # If the action fails, we probably don't want to log "CREATED".
        # So we let the caller commit.
    except Exception as e:
        # Log the error properly instead of swallowing it
        SystemLog.error(
            f"Failed to create audit log: {e}",
            source="AUDIT",
            context={
                "user_id": user_id,
                "action": action,
                "target_type": target_type,
                "target_id": target_id,
            },
        )
