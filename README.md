# 🏥 OCR Medical Insurance Document Extraction System

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)
[![Gemini](https://img.shields.io/badge/Google-Gemini-orange.svg)](https://ai.google.dev/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Hệ thống trích xuất thông tin tự động từ biểu mẫu bảo hiểm y tế 4 trang sử dụng **Gemini Vision API**, **PostgreSQL**, **Redis Cache** và **Prometheus/Grafana Monitoring**.

## 📸 Screenshots

### Dashboard Monitoring (Grafana)
![Grafana Dashboard](docs/images/DashboardGrafana.png)
*Real-time monitoring với Prometheus và Grafana*

### Frontend Testing Results

<div align="center">
  <img src="docs/images/anhTest1.png" width="45%" alt="Test 1" />
  <img src="docs/images/anhTest2.png" width="45%" alt="Test 2" />
</div>

<div align="center">
  <img src="docs/images/anhTest3.png" width="45%" alt="Test 3" />
  <img src="docs/images/anhTest4.png" width="45%" alt="Test 4" />
</div>

*Kết quả test trích xuất thông tin từ biểu mẫu 4 trang*

---

## 🌟 Features

- ✅ **OCR Extraction** - Trích xuất thông tin từ PDF 4 trang với Gemini Vision API
- 🗄️ **Database Storage** - Lưu trữ dữ liệu với Neon PostgreSQL (Cloud)
- 🚀 **Redis Caching** - Cache kết quả với Redis Cloud (tăng tốc 10x)
- 📊 **Monitoring** - Prometheus metrics + Grafana dashboard
- 🔍 **Data Validation** - Kiểm tra và validate dữ liệu trích xuất
- 📝 **Audit Logs** - Lưu lại lịch sử xử lý
- 🎨 **Image Preprocessing** - Tự động cải thiện chất lượng ảnh
- ⚡ **Fast Processing** - Xử lý 4 trang trong ~55 giây

---

## 📋 Table of Contents

- [Architecture](#-architecture)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Monitoring](#-monitoring)
- [Project Structure](#-project-structure)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🏗️ Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Frontend  │─────▶│   FastAPI    │─────▶│   Gemini    │
│   (React)   │      │   Backend    │      │  Vision API │
└─────────────┘      └──────────────┘      └─────────────┘
                            │
                            ├─────▶ PostgreSQL (Neon Cloud)
                            │
                            ├─────▶ Redis (Redis Cloud)
                            │
                            └─────▶ Prometheus ──▶ Grafana
```

### Data Flow:
1. User uploads PDF → Backend
2. Check Redis cache → If hit, return cached
3. Convert PDF to images (PyMuPDF)
4. Extract with Gemini Vision API (4 pages)
5. Validate & merge data
6. Save to PostgreSQL
7. Cache result in Redis
8. Return JSON response

---

## 🔧 Prerequisites

### Required:
- **Python 3.11+**
- **Conda** (Miniconda or Anaconda)
- **Google Gemini API Key** ([Get here](https://makersuite.google.com/app/apikey))
- **Neon PostgreSQL Account** ([Sign up](https://neon.tech))
- **Redis Cloud Account** ([Sign up](https://redis.com/try-free/))

### Optional:
- **Docker** (for Prometheus/Grafana)
- **Git**

---

## 📦 Installation

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/ocr-insurance-document.git
cd ocr-insurance-document
```

### Step 2: Create Conda Environment

```bash
# Create conda environment with Python 3.11
conda create -n ocr_insurance_document python=3.11 --y

# Activate environment
conda activate ocr_insurance_document

# Verify Python version
python --version
# Should output: Python 3.11.x
```

### Step 3: Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Verify installations
pip list | grep -E "fastapi|PyMuPDF|google-generativeai"
```

**requirements.txt:**
```txt
# FastAPI & Web Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6

# PDF & Image Processing
PyMuPDF==1.23.8
Pillow==10.1.0
opencv-python==4.8.1.78

# AI
google-generativeai==0.3.1

# Database
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
alembic==1.12.1

# Cache
redis==5.0.1

# Utilities
python-dotenv==1.0.0
pydantic-settings==2.1.0
httpx==0.25.2

# Monitoring
prometheus-client==0.19.0
```

---

## ⚙️ Configuration

### Step 1: Get Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with Google Account
3. Click **"Create API Key"**
4. Copy the API key (starts with `AIzaSy...`)

### Step 2: Setup Neon PostgreSQL (Cloud)

1. Sign up at [Neon.tech](https://neon.tech)
2. Create new project
3. Copy connection string:
   ```
   postgresql://username:password@ep-xxx-pooler.aws.neon.tech/dbname?sslmode=require
   ```

### Step 3: Setup Redis Cloud (Free Tier)

1. Sign up at [Redis Cloud](https://redis.com/try-free/)
2. Create new database (30MB free)
3. Copy connection string:
   ```
   redis://default:password@redis-12345.cloud.redislabs.com:12345
   ```

### Step 4: Create `.env` File

```bash
# Create .env file in project root
cat > .env << 'EOF'
# ===========================
# Application
# ===========================
APP_NAME=OCR Medical Document API
APP_URL=http://localhost:8000

# ===========================
# Gemini AI
# ===========================
GEMINI_API_KEY=AIzaSy_your_actual_key_here

# ===========================
# Database - Neon PostgreSQL
# ===========================
DATABASE_URL=postgresql://username:password@ep-xxx-pooler.ap-southeast-1.aws.neon.tech/dbname?sslmode=require&channel_binding=require

# ===========================
# Redis - Redis Cloud
# ===========================
REDIS_URL=redis://default:password@redis-12345.c1.us-east-1-2.ec2.cloud.redislabs.com:12345

# ===========================
# Settings
# ===========================
MAX_FILE_SIZE=10485760
PDF_DPI=300
MAX_PAGES=4
RATE_LIMIT_DELAY=1.0
EOF
```

### Step 5: Initialize Database

```bash
# Create database tables
python -c "from src.database import init_db; init_db()"
```

Expected output:
```
✓ Using database: ep-xxx-pooler.ap-southeast-1.aws.neon.tech
✓ Database tables created successfully
✓ Database connection test successful
✅ Database ready!
```

### Step 6: Test Connections

```bash
# Test all connections
python test_connections.py
```

Expected output:
```
🔍 Testing connections...

✅ Database: Connected
✅ Redis: Connected
✅ Gemini API: Configured

==================================================
✅ System ready!
```

---

## 🚀 Usage

### Start Backend Server

```bash
# Activate conda environment
conda activate ocr_insurance_document

# Start FastAPI server
uvicorn src:app --reload --host 0.0.0.0 --port 8000
```

Server will start at: **http://localhost:8000**

### API Endpoints

Access interactive API docs: **http://localhost:8000/docs**

### Upload PDF via cURL

```bash
curl -X POST "http://localhost:8000/api/v1/ocr/extract-multipage" \
  -F "file=@your-medical-form.pdf"
```

### Example Response

```json
{
  "total_pages": 4,
  "merged_data": {
    "policy_details": {
      "policy_no": "P123456",
      "policyowner_name": "John Doe"
    },
    "insured_info": {
      "name": "John Doe",
      "occupation": "Teacher",
      "id_passport": "A1234567",
      "date_of_birth": "01/01/1980",
      "sex": "Male"
    },
    "benefits_to_claim": ["Medical Reimbursement"],
    "payment_instructions": {
      "payment_method": "e-Payout",
      "account_holder_name": "John Doe",
      "bank_name": "ABC Bank",
      "account_number": "123456789"
    },
    "declaration": {
      "signatory_name": "John Doe",
      "signature_date": "15/01/2025",
      "has_signature": true
    },
    "physician_report": {
      "patient_name": "John Doe",
      "admission_date": "10/01/2025",
      "discharge_date": "12/01/2025",
      "final_diagnosis": "Common Cold",
      "operation_procedures": ["Blood Test"],
      "mode_of_anaesthesia": "None"
    }
  },
  "processing_time": 15.2,
  "document_id": 1,
  "extraction_id": 1,
  "cache_hit": false
}
```

---

## 📚 API Documentation

### Main Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/ocr/extract-multipage` | Extract from 4-page PDF |
| POST | `/api/v1/ocr/preview-pages` | Preview PDF pages as images |
| GET | `/api/v1/ocr/extraction/{id}` | Get extraction by ID |
| GET | `/api/v1/ocr/stats` | System statistics |
| GET | `/api/v1/ocr/health` | Health check |


### Monitoring

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/metrics` | Prometheus metrics |
| GET | `/api/v1/ocr/health` | Health check |

---

## 📊 Monitoring

### Prometheus + Grafana Setup

```bash
# Start monitoring stack
docker-compose -f docker-compose.monitoring.yml up -d
```

### Access Dashboards

- **Grafana**: http://localhost:3001
  - Username: `admin`
  - Password: `admin123`
  
- **Prometheus**: http://localhost:9090

- **Metrics**: http://localhost:8000/metrics

### Key Metrics

- **API Request Rate**: `rate(api_requests_total[5m])`
- **Processing Time P95**: `histogram_quantile(0.95, rate(ocr_processing_duration_seconds_bucket[5m]))`
- **Cache Hit Rate**: `cache_hits_total / (cache_hits_total + cache_misses_total) * 100`
- **Success Rate**: `sum(rate(ocr_extractions_total{status="completed"}[5m])) / sum(rate(ocr_extractions_total[5m])) * 100`

---

## 📁 Project Structure

```
ocr-insurance-document/
├── frontend/                      # React frontend
│   ├── src/
│   ├── public/
│   └── package.json
├── src/                          # Backend source
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   └── upload.py     # Main API endpoints
│   │       └── router.py
│   ├── cache/
│   │   └── redis_client.py       # Redis cache manager
│   ├── database/
│   │   ├── models.py             # SQLAlchemy models
│   │   ├── schemas.py            # Pydantic schemas
│   │   └── crud.py               # Database operations
│   ├── extraction/
│   │   ├── extractor.py          # Gemini extractor
│   │   └── preprocessor.py       # Image preprocessing
│   ├── ocr/
│   │   ├── processor.py          # PDF processor
│   │   └── quality_checker.py    # Quality check
│   ├── monitoring/
│   │   └── __init__.py           # Prometheus metrics
│   ├── settings/
│   │   ├── __init__.py           # Configuration
│   │   └── prompts/
│   │       └── __init__.py       # Gemini prompts
│   ├── utils/
│   │   ├── merger.py             # Result merger
│   │   ├── validator.py          # Data validator
│   │   ├── metrics.py            # Metrics collector
│   │   └── logger.py             # Logging
│   ├── WrapperFunction/
│   │   └── __init__.py           # Helper functions
│   └── __init__.py               # FastAPI app
├── monitoring/
│   ├── prometheus.yml            # Prometheus config
│   └── grafana/
│       └── dashboards/
│           └── ocr-dashboard.json
├── docs/
│   └── images/                   # Screenshots
│       ├── DashboardGrafana.png
│       ├── anhTest1.png
│       ├── anhTest2.png
│       ├── anhTest3.png
│       └── anhTest4.png
├── tests/                        # Test files
├── .env.example                  # Environment template
├── .gitignore
├── requirements.txt
├── docker-compose.yml
├── docker-compose.monitoring.yml
├── Makefile
└── README.md
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. Redis Connection Failed

```bash
# Error: getaddrinfo failed connecting to redis:6379

# Fix: Update .env
REDIS_URL=redis://localhost:6379/0  # For local Redis
# OR
REDIS_URL=redis://default:pass@your-redis-cloud.com:12345  # For Redis Cloud
```

#### 2. Database Connection Failed

```bash
# Error: could not connect to server

# Fix: Check DATABASE_URL in .env
# Make sure to include ?sslmode=require for Neon
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require
```

#### 3. Gemini API Error

```bash
# Error: API key not valid

# Fix: Check GEMINI_API_KEY in .env
# Get new key from: https://makersuite.google.com/app/apikey
```

#### 4. Import Error

```bash
# Error: ModuleNotFoundError: No module named 'src'

# Fix: Make sure you're in project root
cd /path/to/ocr-insurance-document

# And conda environment is activated
conda activate ocr_insurance_document
```

#### 5. PyMuPDF/OpenCV Error

```bash
# For macOS M1/M2
conda install -c conda-forge pymupdf opencv

# For Linux
sudo apt-get install python3-opencv
```

---

## 🧪 Testing

### Run Tests

```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# All tests
pytest
```

### Test with Sample PDF

```bash
# Upload test document
curl -X POST "http://localhost:8000/api/v1/ocr/extract-multipage" \
  -F "file=@tests/fixtures/sample_medical_form.pdf"

# Check health
curl http://localhost:8000/api/v1/ocr/health

# View stats
curl http://localhost:8000/api/v1/ocr/stats

# View cache
curl http://localhost:8000/api/v1/ocr/cache/info
```

---

## 🔒 Security

- ✅ API keys stored in `.env` (not in code)
- ✅ Database connections use SSL
- ✅ Input validation on all endpoints
- ✅ File size limits enforced
- ✅ SQL injection protection (SQLAlchemy ORM)
- ✅ CORS configured

---

## 📈 Performance

- **Processing Time**: ~15 seconds for 4-page PDF
- **Cache Hit**: <100ms response time
- **Database**: <50ms query time
- **Throughput**: 10+ documents/minute
- **Memory**: ~500MB average

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Authors

- **Your Name** - *Initial work* - [YourGitHub](https://github.com/yourusername)

---

## 🙏 Acknowledgments

- [Google Gemini](https://ai.google.dev/) - Vision API
- [Neon](https://neon.tech) - PostgreSQL Database
- [Redis Cloud](https://redis.com) - Redis Cache
- [FastAPI](https://fastapi.tiangolo.com/) - Web Framework
- [PyMuPDF](https://pymupdf.readthedocs.io/) - PDF Processing

---

## 📞 Support

- **Documentation**: [Wiki](https://github.com/yourusername/ocr-insurance-document/wiki)
- **Issues**: [GitHub Issues](https://github.com/yourusername/ocr-insurance-document/issues)
- **Email**: your.email@example.com

---

## 🎯 Roadmap

- [ ] Support more document types (invoices, receipts)
- [ ] Multi-language support
- [ ] Batch processing
- [ ] Web-based admin dashboard
- [ ] Export to Excel/PDF
- [ ] Email notifications
- [ ] User authentication

---

## 📊 Stats

![GitHub stars](https://img.shields.io/github/stars/yourusername/ocr-insurance-document?style=social)
![GitHub forks](https://img.shields.io/github/forks/yourusername/ocr-insurance-document?style=social)
![GitHub issues](https://img.shields.io/github/issues/yourusername/ocr-insurance-document)
![GitHub pull requests](https://img.shields.io/github/issues-pr/yourusername/ocr-insurance-document)

---

<div align="center">
  <strong>Made with ❤️ by Your Team</strong>
  
  ⭐ Star us on GitHub — it helps!
</div>