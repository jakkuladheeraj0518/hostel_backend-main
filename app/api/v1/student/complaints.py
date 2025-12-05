from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Header
from sqlalchemy.orm import Session
from typing import Optional
from pathlib import Path
import aiofiles
import uuid
 
from app.core.database import get_db
from app.core.roles import Role
from app.core.permissions import Permission
from app.api.deps import role_required, permission_required, get_current_active_user, get_repository_context, get_user_hostel_ids
from app.core.exceptions import AccessDeniedException
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse, AdminCreate
from app.repositories.user_repository import UserRepository
from app.services.permission_service import PermissionService
from app.core.security import get_password_hash
from app.models.complaint import ComplaintStatus
from app.repositories.complaint_repository import ComplaintRepository
from app.services.complaint_service import ComplaintService
from app.schemas.complaint import (
    ComplaintCreate,
    ComplaintResponse,
    ComplaintDetailResponse,
    ComplaintListResponse,
    ComplaintFilter,
    ComplaintFeedback,
    ComplaintReopen,
    ComplaintNoteCreate
)
from app.config import settings
from sqlalchemy import select
from app.models.hostel import Hostel
from app.models.students import Student
 
router = APIRouter(prefix="/student/complaints", tags=["Student Complaints"])
 
 
@router.post("/", response_model=ComplaintResponse, status_code=status.HTTP_201_CREATED)
async def create_complaint(
    complaint_data: ComplaintCreate,
    current_user: User = Depends(role_required(Role.STUDENT)),
    db: Session = Depends(get_db)
):
    """Submit a new complaint"""
    # If caller provided a hostel_id, resolve it to hostel_name and validate existence.
    payload = complaint_data.model_dump()
    hostel_id = payload.get('hostel_id') if isinstance(payload, dict) else None
    student_id = payload.get('student_id')
   
    # Require hostel_id in the new schema (hostel_name replaced by hostel_id).
    if hostel_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="hostel id not found")
 
    if hostel_id is not None:
        # `get_db` yields a synchronous Session; execute synchronously to avoid awaiting a non-awaitable
        result = db.execute(select(Hostel).where(Hostel.id == int(hostel_id)))
        hostel = result.scalar_one_or_none()
        if not hostel:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="hostel id not found")
        # Set hostel_name and keep hostel_id for database storage
        payload['hostel_name'] = hostel.hostel_name
        payload['hostel_id'] = int(hostel_id)
   
    # Validate student_id if provided
    if student_id is not None:
        result = db.execute(select(Student).where(Student.student_id == str(student_id)))
        student = result.scalar_one_or_none()
        if not student:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="student id not found")
 
    repository = ComplaintRepository(db)
    service = ComplaintService(repository)
 
    # Pass a plain dict payload that includes `hostel_name` so the repository
    # gets the expected field for DB insertion.
    try:
        complaint = await service.create_complaint(payload)
        return complaint
    except ValueError as e:
        # Map service validation errors to HTTP responses
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
 
 
@router.get("/", response_model=ComplaintListResponse)
async def list_student_complaints(
    student_email: str = Header(..., alias="X-User-Email"),
    hostel_name: Optional[str] = None,
    category: Optional[str] = None,
    status_filter: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
    current_user: User = Depends(role_required(Role.STUDENT)),
    db: Session = Depends(get_db)
):
    """List complaints by student email"""
    filters = ComplaintFilter(
        student_email=student_email,
        hostel_name=hostel_name,
        category=category,
        status=status_filter,
        page=page,
        page_size=page_size
    )
   
    repository = ComplaintRepository(db)
    service = ComplaintService(repository)
   
    complaints, total = await service.list_complaints(filters)
   
    total_pages = (total + page_size - 1) // page_size
   
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "complaints": complaints
    }
 
 
@router.get("/{complaint_id}", response_model=ComplaintDetailResponse)
async def get_complaint(
    complaint_id: int,
    student_email: str = Header(..., alias="X-User-Email"),
    current_user: User = Depends(role_required(Role.STUDENT)),
    db: Session = Depends(get_db)
):
    """Get complaint details with attachments and notes"""
    repository = ComplaintRepository(db)
    service = ComplaintService(repository)
   
    result = await service.get_complaint_with_details(complaint_id)
   
    if not result:
        raise HTTPException(status_code=404, detail="Complaint not found")
   
    complaint = result["complaint"]
   
    # Verify student owns the complaint
    if complaint.student_email != student_email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own complaints"
        )
   
    return {
        **complaint.__dict__,
        "attachments": result["attachments"],
        "notes": result["notes"]
    }
 
 
@router.post("/{complaint_id}/attachments", status_code=status.HTTP_201_CREATED)
async def upload_attachment(
    complaint_id: int,
    file: UploadFile = File(...),
    student_email: str = Header(..., alias="X-User-Email"),
    current_user: User = Depends(role_required(Role.STUDENT)),
    db: Session = Depends(get_db)
):
    """Upload attachment for a complaint"""
    repository = ComplaintRepository(db)
    service = ComplaintService(repository)
   
    complaint = await service.get_complaint(complaint_id)
   
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
   
    if complaint.student_email != student_email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only upload attachments to your own complaints"
        )
   
    # Validate file size
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
   
    if file_size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE} bytes"
        )
   
    # Create upload directory
    upload_dir = Path(settings.UPLOAD_DIR) / str(complaint_id)
    upload_dir.mkdir(parents=True, exist_ok=True)
   
    # Generate unique filename
    file_extension = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = upload_dir / unique_filename
   
    # Save file
    async with aiofiles.open(file_path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)
   
    # Save attachment record
    attachment = await service.add_attachment(
        complaint_id=complaint_id,
        uploaded_by=student_email,
        file_path=str(file_path),
        file_name=file.filename,
        file_type=file.content_type or 'application/octet-stream',
        file_size=file_size
    )
   
    return {
        "message": "File uploaded successfully",
        "attachment_id": attachment.id,
        "file_name": file.filename
    }
 
 
@router.post("/{complaint_id}/feedback", response_model=ComplaintResponse)
async def submit_feedback(
    complaint_id: int,
    feedback_data: ComplaintFeedback,
    student_email: str = Header(..., alias="X-User-Email"),
    current_user: User = Depends(role_required(Role.STUDENT)),
    db: Session = Depends(get_db)
):
    """Submit feedback for a resolved complaint"""
    repository = ComplaintRepository(db)
    service = ComplaintService(repository)
   
    complaint = await service.get_complaint(complaint_id)
   
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
   
    if complaint.student_email != student_email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only submit feedback for your own complaints"
        )
   
    if complaint.status not in [ComplaintStatus.RESOLVED, ComplaintStatus.CLOSED]:
        raise HTTPException(
            status_code=400,
            detail="Feedback can only be submitted for resolved complaints"
        )
   
    complaint = await service.submit_feedback(complaint_id, feedback_data)
    return complaint
 
 
@router.post("/{complaint_id}/reopen", response_model=ComplaintResponse)
async def reopen_complaint(
    complaint_id: int,
    reopen_data: ComplaintReopen,
    student_email: str = Header(..., alias="X-User-Email"),
    current_user: User = Depends(role_required(Role.STUDENT)),
    db: Session = Depends(get_db)
):
    """Reopen a closed complaint"""
    repository = ComplaintRepository(db)
    service = ComplaintService(repository)
   
    complaint = await service.get_complaint(complaint_id)
   
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
   
    if complaint.student_email != student_email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only reopen your own complaints"
        )
   
    try:
        complaint = await service.reopen_complaint(complaint_id, reopen_data)
        return complaint
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
 
 
@router.post("/{complaint_id}/notes", status_code=status.HTTP_201_CREATED)
async def add_note(
    complaint_id: int,
    note: str,
    student_name: str = Header(..., alias="X-User-Name"),
    student_email: str = Header(..., alias="X-User-Email"),
    current_user: User = Depends(role_required(Role.STUDENT)),
    db: Session = Depends(get_db)
):
    """Add a note to the complaint"""
    repository = ComplaintRepository(db)
    service = ComplaintService(repository)
   
    complaint = await service.get_complaint(complaint_id)
   
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
   
    if complaint.student_email != student_email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only add notes to your own complaints"
        )
   
    note_data = ComplaintNoteCreate(
        note=note,
        user_name=student_name,
        user_email=student_email,
        is_internal=False
    )
   
    created_note = await service.add_note(complaint_id, note_data)
   
    return {
        "message": "Note added successfully",
        "note_id": created_note.id
    }