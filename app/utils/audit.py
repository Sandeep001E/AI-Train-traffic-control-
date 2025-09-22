from typing import Optional, Any
from sqlalchemy.orm import Session
from app.models.audit import AuditLog

def record_audit(
    db: Session,
    action: str,
    entity_type: str,
    entity_id: Optional[str] = None,
    details: Optional[Any] = None,
    actor_user_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
):
    log = AuditLog(
        actor_user_id=actor_user_id,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id) if entity_id is not None else None,
        details=details,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.add(log)
    db.commit()
    return log
