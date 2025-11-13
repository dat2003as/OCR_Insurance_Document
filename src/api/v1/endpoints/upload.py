"""
Upload and Processing Endpoints
"""
import hashlib
import time
from venv import logger
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict, Any
from fastapi.params import Depends
from pydantic import BaseModel

from src.ocr.processor import PDFProcessor
from src.extraction.extractor import GeminiExtractor
from src.utils.merger import ResultMerger  
from src.utils.validator import DataValidator  
from src.settings import APP_SETTINGS
from src.database import get_db
from src.database.crud import DocumentCRUD, ExtractionCRUD, AuditLogCRUD
from src.database.models import Document, Extraction
from src.cache.redis_client import CacheManager
from sqlalchemy.orm import Session
from datetime import datetime
from src.monitoring import (
    track_ocr_metrics,
    record_cache_hit,
    record_cache_miss,
    record_db_query,
    update_system_gauges,
    ocr_pages_processed,
    ocr_extractions_total,
    api_requests_total,
    errors_total
)
router = APIRouter()

class ExtractionResponse(BaseModel):
    total_pages: int
    merged_data: Dict[str, Any]
    page_results: list
    processing_method: str
    validation_errors: Dict[str, Any] = {}
    # New fields
    document_id: int = None
    extraction_id: int = None
    processing_time: float = None
    cache_hit: bool = False


@router.post("/extract-multipage", response_model=ExtractionResponse)
@track_ocr_metrics()  # Prometheus decorator
async def extract_multipage_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Extract structured data from 4-page medical claim form
    Features: Redis Cache + Prometheus Metrics + Database Storage
    """
    start_time = time.time()
    
    # Validate file
    if not file.filename.endswith('.pdf'):
        api_requests_total.labels(
            method='POST',
            endpoint='/extract-multipage',
            status=400
        ).inc()
        raise HTTPException(status_code=400, detail="Only PDF files supported")
    
    try:
        # Read file
        pdf_bytes = await file.read()
        file_size = len(pdf_bytes)
        
        # Validate file size
        if file_size > APP_SETTINGS.MAX_FILE_SIZE:
            api_requests_total.labels(
                method='POST',
                endpoint='/extract-multipage',
                status=400
            ).inc()
            raise HTTPException(status_code=400, detail="File too large")
        
        # Calculate file hash for cache/deduplication
        file_hash = hashlib.md5(pdf_bytes).hexdigest()
        cache_key = f"extraction:{file_hash}"
        
        #CHECK REDIS CACHE FIRST
        cache = CacheManager()
        cached_result = cache.get_cached_extraction(cache_key)
        
        if cached_result:
            logger.info(f"✅ Cache hit for file: {file.filename}")
            record_cache_hit()  # Prometheus metric
            
            api_requests_total.labels(
                method='POST',
                endpoint='/extract-multipage',
                status=200
            ).inc()
            
            cached_result["cache_hit"] = True
            return ExtractionResponse(**cached_result)
        
        # Cache miss
        record_cache_miss()  # Prometheus metric
        logger.info(f"⚠️  Cache miss for file: {file.filename}")
        
        # CHECK DATABASE FOR EXISTING DOCUMENT 
        db_query_start = time.time()
        existing_doc = DocumentCRUD.get_by_hash(db, file_hash)
        record_db_query('select', time.time() - db_query_start)
        
        if existing_doc and existing_doc.processed:
            logger.info(f"♻️  Document already processed: {existing_doc.id}")
            
            # Get existing extraction
            extractions = ExtractionCRUD.list_by_document(db, existing_doc.id)
            if extractions:
                extraction = extractions[0]
                
                response_data = {
                    "total_pages": extraction.total_pages,
                    "merged_data": {
                        "policy_details": extraction.policy_details or {},
                        "insured_info": extraction.insured_info or {},
                        "benefits_to_claim": extraction.benefits_to_claim or [],
                        "payment_instructions": extraction.payment_instructions or {},
                        "declaration": extraction.declaration or {},
                        "physician_report": extraction.physician_report or {}
                    },
                    "page_results": [],
                    "processing_method": "PyMuPDF + Gemini Vision API",
                    "validation_errors": extraction.validation_errors or {},
                    "document_id": existing_doc.id,
                    "extraction_id": extraction.id,
                    "processing_time": extraction.processing_time,
                    "cache_hit": False
                }
                
                # Cache for next time
                cache.cache_extraction(cache_key, response_data, ttl=3600)
                
                return ExtractionResponse(**response_data)
        
        # SAVE DOCUMENT TO DATABASE
        
        db_insert_start = time.time()
        doc = DocumentCRUD.create(
            db,
            filename=file.filename,
            file_path=f"uploads/{file.filename}",
            file_size=file_size,
            file_content=pdf_bytes
        )
        record_db_query('insert', time.time() - db_insert_start)
        
        # Create extraction record
        extraction = ExtractionCRUD.create(
            db,
            document_id=doc.id,
            workflow="ocr_only"
        )
        
        # Update to processing
        ExtractionCRUD.update(
            db,
            extraction.id,
            status="processing",
            started_at=datetime.utcnow()
        )
        
        # Audit log
        AuditLogCRUD.create(
            db,
            extraction_id=extraction.id,
            action="extraction_started",
            changes={"filename": file.filename}
        )
        
        # PROCESS PDF 
        processor = PDFProcessor()
        processor.validate_pdf(pdf_bytes)
        images = processor.pdf_to_images(pdf_bytes)
        
        # Prometheus: Record pages
        ocr_pages_processed.inc(len(images))
        
        #EXTRACT WITH GEMINI 
        extractor = GeminiExtractor()
        page_results = await extractor.extract_multipage(images)
        
        # VALIDATE AND CLEAN 
        logger.info("✔️  Validating data...")
        validated_results = [
            DataValidator.validate_extracted_data(result) 
            for result in page_results
        ]
        
        # 
        # MERGE RESULTS 
        logger.info("🔗 Merging page results...")
        merged_data = ResultMerger.merge_results(validated_results)
        
        #VALIDATE COMPLETE FORM
        validation_errors = DataValidator.validate_medical_form(merged_data)
        
        # Format response (Original logic)
        formatted_results = [
            {
                "page_number": i + 1,
                "extracted_data": result,
                "confidence": "high" if "error" not in result else "low"
            }
            for i, result in enumerate(validated_results)
        ]
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        #UPDATE DATABASE WITH RESULTs        
        db_update_start = time.time()
        ExtractionCRUD.update(
            db,
            extraction.id,
            status="completed",
            policy_details=merged_data.get("policy_details"),
            insured_info=merged_data.get("insured_info"),
            benefits_to_claim=merged_data.get("benefits_to_claim"),
            payment_instructions=merged_data.get("payment_instructions"),
            declaration=merged_data.get("declaration"),
            physician_report=merged_data.get("physician_report"),
            total_pages=len(images),
            processing_time=processing_time,
            validation_errors=validation_errors,
            completed_at=datetime.utcnow()
        )
        record_db_query('update', time.time() - db_update_start)
        
        # Update document status
        DocumentCRUD.update_status(db, doc.id, "completed")
        
        # Audit log
        AuditLogCRUD.create(
            db,
            extraction_id=extraction.id,
            action="extraction_completed",
            changes={
                "processing_time": processing_time,
                "pages": len(images)
            }
        )
        
        #UPDATE PROMETHEUS SYSTEM GAUGES
        total_docs = db.query(Document).count()
        total_extractions = db.query(Extraction).count()
        update_system_gauges(total_docs, total_extractions)
        
        # Prometheus: Record success
        ocr_extractions_total.labels(status='completed').inc()
        
        logger.info(f"✅ Extraction completed in {processing_time:.2f}s")
        
        # 11. BUILD RESPONSE
        response_data = {
            "total_pages": len(images),
            "merged_data": merged_data,
            "page_results": formatted_results,
            "processing_method": "PyMuPDF + Gemini Vision API",
            "validation_errors": validation_errors,
            "document_id": doc.id,
            "extraction_id": extraction.id,
            "processing_time": processing_time,
            "cache_hit": False
        }
        
        # CACHE RESULT
        cache.cache_extraction(cache_key, response_data, ttl=3600)
        logger.info("💾 Result cached")
        
        # Prometheus: Record API success
        api_requests_total.labels(
            method='POST',
            endpoint='/extract-multipage',
            status=200
        ).inc()
        
        return ExtractionResponse(**response_data)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Extraction failed: {str(e)}", exc_info=True)
        
        # Prometheus: Record error
        errors_total.labels(error_type=type(e).__name__).inc()
        ocr_extractions_total.labels(status='failed').inc()
        
        # Update extraction status if exists
        if 'extraction' in locals():
            ExtractionCRUD.update(
                db,
                extraction.id,
                status="failed",
                completed_at=datetime.utcnow()
            )
            
            AuditLogCRUD.create(
                db,
                extraction_id=extraction.id,
                action="extraction_failed",
                changes={"error": str(e)}
            )
        
        api_requests_total.labels(
            method='POST',
            endpoint='/extract-multipage',
            status=500
        ).inc()
        
        raise HTTPException(status_code=500, detail=str(e))






@router.get("/extraction/{extraction_id}")
async def get_extraction(
    extraction_id: int,
    db: Session = Depends(get_db)
):
    """Get extraction by ID (with cache check)"""
    
    try:
        # Check cache first
        cache = CacheManager()
        cache_key = f"extraction:id:{extraction_id}"
        cached = cache.get_cached_extraction(cache_key)
        
        if cached:
            record_cache_hit()
            return {"source": "cache", "data": cached}
        
        record_cache_miss()
        
        # Get from database
        db_query_start = time.time()
        extraction = ExtractionCRUD.get(db, extraction_id)
        record_db_query('select', time.time() - db_query_start)
        
        if not extraction:
            api_requests_total.labels(
                method='GET',
                endpoint='/extraction',
                status=404
            ).inc()
            raise HTTPException(status_code=404, detail="Extraction not found")
        
        result = extraction.to_dict()
        
        # Cache it
        if extraction.status == "completed":
            cache.cache_extraction(cache_key, result, ttl=3600)
        
        api_requests_total.labels(
            method='GET',
            endpoint='/extraction',
            status=200
        ).inc()
        
        return {"source": "database", "data": result}
    
    except HTTPException:
        raise
    except Exception as e:
        errors_total.labels(error_type=type(e).__name__).inc()
        raise
@router.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Get system statistics"""
    
    try:
        db_query_start = time.time()
        
        total_documents = db.query(Document).count()
        processed_documents = db.query(Document).filter(Document.processed == True).count()
        total_extractions = db.query(Extraction).count()
        completed_extractions = db.query(Extraction).filter(Extraction.status == "completed").count()
        failed_extractions = db.query(Extraction).filter(Extraction.status == "failed").count()
        
        record_db_query('select', time.time() - db_query_start)
        
        # Update gauges
        update_system_gauges(total_documents, total_extractions)
        
        api_requests_total.labels(
            method='GET',
            endpoint='/stats',
            status=200
        ).inc()
        
        return {
            "database": {
                "total_documents": total_documents,
                "processed_documents": processed_documents,
                "total_extractions": total_extractions,
                "completed_extractions": completed_extractions,
                "failed_extractions": failed_extractions,
                "success_rate": f"{(completed_extractions/total_extractions*100 if total_extractions > 0 else 0):.1f}%"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        errors_total.labels(error_type=type(e).__name__).inc()
        raise

@router.get("/cache/info")
async def get_cache_info():
    """Get cache information and statistics"""
    try:
        cache = CacheManager()
        
        # Get all extraction keys
        extraction_keys = cache.redis.keys('extraction:*')
        
        # Get Redis info
        redis_info = cache.redis.info()
        
        # Sample keys (first 5)
        sample_keys = []
        for key in extraction_keys[:5]:
            key_str = key.decode() if isinstance(key, bytes) else key
            ttl = cache.redis.ttl(key)
            
            # Get size
            try:
                size = len(cache.redis.get(key) or b'')
            except:
                size = 0
            
            sample_keys.append({
                "key": key_str,
                "ttl_seconds": ttl,
                "ttl_minutes": round(ttl / 60, 1) if ttl > 0 else 0,
                "size_bytes": size
            })
        
        api_requests_total.labels(
            method='GET',
            endpoint='/cache/info',
            status=200
        ).inc()
        
        return {
            "total_cached_extractions": len(extraction_keys),
            "redis_version": redis_info.get('redis_version'),
            "used_memory_human": redis_info.get('used_memory_human'),
            "total_keys_in_db": redis_info.get('db0', {}).get('keys', 0) if 'db0' in redis_info else 0,
            "sample_keys": sample_keys,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        errors_total.labels(error_type=type(e).__name__).inc()
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    
    try:
        # Check database
        try:
            db.execute("SELECT 1")
            db_status = "healthy"
        except:
            db_status = "unhealthy"
        
        # Check Redis
        try:
            cache = CacheManager()
            cache.redis.ping()
            redis_status = "healthy"
        except:
            redis_status = "unhealthy"
        
        # Check Gemini
        gemini_status = "configured" if APP_SETTINGS.GEMINI_API_KEY else "not configured"
        
        api_requests_total.labels(
            method='GET',
            endpoint='/health',
            status=200
        ).inc()
        
        return {
            "status": "healthy" if db_status == "healthy" else "degraded",
            "components": {
                "database": db_status,
                "redis": redis_status,
                "gemini_api": gemini_status
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        errors_total.labels(error_type=type(e).__name__).inc()
        return {"status": "unhealthy", "error": str(e)}
