"""
Prometheus Metrics Collection
"""
from prometheus_client import Counter, Histogram, Gauge
from functools import wraps
import time

# =====================
# Metrics Definitions
# =====================

# API Request Metrics
api_requests_total = Counter(
    'api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status']
)

api_request_duration = Histogram(
    'api_request_duration_seconds',
    'API request duration',
    ['method', 'endpoint']
)

# OCR Processing Metrics
ocr_extractions_total = Counter(
    'ocr_extractions_total',
    'Total OCR extractions',
    ['status']  # completed, failed
)

ocr_processing_duration = Histogram(
    'ocr_processing_duration_seconds',
    'OCR processing duration',
    buckets=[1, 5, 10, 30, 60, 120, 300]
)

ocr_pages_processed = Counter(
    'ocr_pages_processed_total',
    'Total pages processed'
)

# Database Metrics
db_queries_total = Counter(
    'db_queries_total',
    'Total database queries',
    ['operation']  # select, insert, update, delete
)

db_query_duration = Histogram(
    'db_query_duration_seconds',
    'Database query duration'
)

# Cache Metrics
cache_hits = Counter('cache_hits_total', 'Total cache hits')
cache_misses = Counter('cache_misses_total', 'Total cache misses')

# System Metrics
active_extractions = Gauge(
    'active_extractions',
    'Currently active extractions'
)

total_documents = Gauge(
    'total_documents',
    'Total documents in database'
)

# Error Metrics
errors_total = Counter(
    'errors_total',
    'Total errors',
    ['error_type']
)

# =====================
# Decorators
# =====================

def track_request_metrics(endpoint: str):
    """Decorator to track API request metrics"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            status = 200
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                status = 500
                errors_total.labels(error_type=type(e).__name__).inc()
                raise
            finally:
                duration = time.time() - start_time
                api_requests_total.labels(
                    method='POST',
                    endpoint=endpoint,
                    status=status
                ).inc()
                api_request_duration.labels(
                    method='POST',
                    endpoint=endpoint
                ).observe(duration)
        
        return wrapper
    return decorator

def track_ocr_metrics():
    """Decorator to track OCR processing metrics"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            active_extractions.inc()
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                
                # Record success metrics
                ocr_extractions_total.labels(status='completed').inc()
                
                # Record processing time
                duration = time.time() - start_time
                ocr_processing_duration.observe(duration)
                
                # Record pages if available
                if 'total_pages' in result:
                    ocr_pages_processed.inc(result['total_pages'])
                
                return result
            
            except Exception as e:
                ocr_extractions_total.labels(status='failed').inc()
                errors_total.labels(error_type=type(e).__name__).inc()
                raise
            
            finally:
                active_extractions.dec()
        
        return wrapper
    return decorator

# =====================
# Helper Functions
# =====================

def record_cache_hit():
    """Record cache hit"""
    cache_hits.inc()

def record_cache_miss():
    """Record cache miss"""
    cache_misses.inc()

def record_db_query(operation: str, duration: float):
    """Record database query"""
    db_queries_total.labels(operation=operation).inc()
    db_query_duration.observe(duration)

def update_system_gauges(doc_count: int, extraction_count: int):
    """Update system gauge metrics"""
    total_documents.set(doc_count)