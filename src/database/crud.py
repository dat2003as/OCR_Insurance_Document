from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
from src.database.models import Document, Extraction, AuditLog
from datetime import datetime
import hashlib


class DocumentCRUD:
    """CRUD operations for documents"""
    
    @staticmethod
    def create(
        db: Session, 
        filename: str, 
        file_path: str, 
        file_size: int,
        file_content: bytes = None
    ) -> Document:
        """Create new document record"""
        # Calculate file hash if content provided
        file_hash = None
        if file_content:
            file_hash = hashlib.md5(file_content).hexdigest()
        
        doc = Document(
            filename=filename,
            original_filename=filename,
            file_path=file_path,
            file_size=file_size,
            file_hash=file_hash,
            status="uploaded"
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        return doc
    
    @staticmethod
    def get(db: Session, doc_id: int) -> Optional[Document]:
        """Get document by ID"""
        return db.query(Document).filter(Document.id == doc_id).first()
    
    @staticmethod
    def get_by_hash(db: Session, file_hash: str) -> Optional[Document]:
        """Get document by file hash (for deduplication)"""
        return db.query(Document).filter(Document.file_hash == file_hash).first()
    
    @staticmethod
    def list(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[str] = None
    ) -> List[Document]:
        """List documents with pagination"""
        query = db.query(Document)
        
        if status:
            query = query.filter(Document.status == status)
        
        return query.order_by(desc(Document.uploaded_at)).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_status(db: Session, doc_id: int, status: str) -> Optional[Document]:
        """Update document status"""
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if doc:
            doc.status = status
            if status == "completed":
                doc.processed = True
                doc.processed_at = datetime.utcnow()
            db.commit()
            db.refresh(doc)
        return doc
    
    @staticmethod
    def delete(db: Session, doc_id: int) -> bool:
        """Delete document"""
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if doc:
            db.delete(doc)
            db.commit()
            return True
        return False


class ExtractionCRUD:
    """CRUD operations for extractions"""
    
    @staticmethod
    def create(
        db: Session, 
        document_id: int, 
        workflow: str = "standard",
        task_id: Optional[str] = None
    ) -> Extraction:
        """Create new extraction record"""
        extraction = Extraction(
            document_id=document_id,
            status="pending",
            agent_workflow=workflow,
            task_id=task_id,
            created_at=datetime.utcnow()
        )
        db.add(extraction)
        db.commit()
        db.refresh(extraction)
        return extraction
    
    @staticmethod
    def get(db: Session, extraction_id: int) -> Optional[Extraction]:
        """Get extraction by ID"""
        return db.query(Extraction).filter(Extraction.id == extraction_id).first()
    
    @staticmethod
    def get_by_task_id(db: Session, task_id: str) -> Optional[Extraction]:
        """Get extraction by Celery task ID"""
        return db.query(Extraction).filter(Extraction.task_id == task_id).first()
    
    @staticmethod
    def update(db: Session, extraction_id: int, **kwargs) -> Optional[Extraction]:
        """Update extraction fields"""
        extraction = db.query(Extraction).filter(Extraction.id == extraction_id).first()
        if extraction:
            for key, value in kwargs.items():
                if hasattr(extraction, key):
                    setattr(extraction, key, value)
            
            # Auto-set completed_at if status is completed
            if kwargs.get('status') == 'completed' and not extraction.completed_at:
                extraction.completed_at = datetime.utcnow()
            
            db.commit()
            db.refresh(extraction)
        return extraction
    
    @staticmethod
    def list_by_status(db: Session, status: str, limit: int = 100) -> List[Extraction]:
        """List extractions by status"""
        return db.query(Extraction)\
            .filter(Extraction.status == status)\
            .order_by(desc(Extraction.created_at))\
            .limit(limit)\
            .all()
    
    @staticmethod
    def list_by_document(db: Session, document_id: int) -> List[Extraction]:
        """List all extractions for a document"""
        return db.query(Extraction)\
            .filter(Extraction.document_id == document_id)\
            .order_by(desc(Extraction.created_at))\
            .all()


class AuditLogCRUD:
    """CRUD operations for audit logs"""
    
    @staticmethod
    def create(
        db: Session,
        extraction_id: int,
        action: str,
        user_id: Optional[str] = None,
        changes: Optional[Dict[str, Any]] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """Create audit log entry"""
        log = AuditLog(
            extraction_id=extraction_id,
            action=action,
            user_id=user_id,
            changes=changes,
            old_values=old_values,
            new_values=new_values,
            timestamp=datetime.utcnow()
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log
    
    @staticmethod
    def list_by_extraction(
        db: Session, 
        extraction_id: int,
        limit: int = 100
    ) -> List[AuditLog]:
        """Get audit logs for an extraction"""
        return db.query(AuditLog)\
            .filter(AuditLog.extraction_id == extraction_id)\
            .order_by(desc(AuditLog.timestamp))\
            .limit(limit)\
            .all()

