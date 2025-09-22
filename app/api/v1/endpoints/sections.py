from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.section import Section
from app.schemas.section import SectionCreate, SectionRead, SectionUpdate
from app.utils.audit import record_audit

router = APIRouter()

@router.get("/ping")
async def ping_sections():
    return {"module": "sections", "status": "ok"}

@router.get("/", response_model=List[SectionRead])
def list_sections(db: Session = Depends(get_db)):
    return db.query(Section).all()

@router.post("/", response_model=SectionRead)
def create_section(payload: SectionCreate, db: Session = Depends(get_db), request: Request = None):
    # Ensure unique section_code
    existing = db.query(Section).filter(Section.section_code == payload.section_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Section code already exists")

    section = Section(**payload.dict())
    db.add(section)
    db.commit()
    db.refresh(section)

    try:
        record_audit(
            db,
            action="create",
            entity_type="section",
            entity_id=section.id,
            details={"section_code": section.section_code},
            ip_address=(request.client.host if request and request.client else None),
            user_agent=(request.headers.get("User-Agent") if request else None)
        )
    except Exception:
        pass

    return section

@router.get("/{section_id}", response_model=SectionRead)
def get_section(section_id: int, db: Session = Depends(get_db)):
    section = db.get(Section, section_id)
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    return section

@router.put("/{section_id}", response_model=SectionRead)
def update_section(section_id: int, payload: SectionUpdate, db: Session = Depends(get_db), request: Request = None):
    section = db.get(Section, section_id)
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")

    data = payload.dict(exclude_unset=True)
    for k, v in data.items():
        setattr(section, k, v)

    db.commit()
    db.refresh(section)

    try:
        record_audit(
            db,
            action="update",
            entity_type="section",
            entity_id=section.id,
            details=data,
            ip_address=(request.client.host if request and request.client else None),
            user_agent=(request.headers.get("User-Agent") if request else None)
        )
    except Exception:
        pass

    return section

@router.delete("/{section_id}")
def delete_section(section_id: int, db: Session = Depends(get_db), request: Request = None):
    section = db.get(Section, section_id)
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    db.delete(section)
    db.commit()

    try:
        record_audit(
            db,
            action="delete",
            entity_type="section",
            entity_id=section_id,
            details=None,
            ip_address=(request.client.host if request and request.client else None),
            user_agent=(request.headers.get("User-Agent") if request else None)
        )
    except Exception:
        pass

    return {"status": "deleted", "id": section_id}
