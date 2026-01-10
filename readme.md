# 🚗 Car Manual RAG System

AI-powered question answering system for car manuals using Retrieval-Augmented Generation (RAG). Ask questions in natural language (Bahasa Indonesia) and get accurate answers with source references.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.29+-red.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16+-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Project Structure](#-project-structure)
- [Configuration](#-configuration)
- [Testing](#-testing)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

### Core Features
- 📄 **PDF Processing**: Extract and process 300+ page car manuals
- 🔍 **Semantic Search**: Vector-based similarity search using embeddings
- 🤖 **AI-Powered Answers**: Natural language responses using Google Gemini
- 🗄️ **Efficient Storage**: PostgreSQL with pgvector extension
- 🐳 **Dockerized**: Complete containerization for easy deployment

### Advanced Features
- 📚 **Multi-Manual Support**: Upload and query multiple manuals
- 🔐 **Duplicate Detection**: SHA256 hash-based deduplication
- ⚡ **Background Processing**: Non-blocking document processing
- 📊 **Source Attribution**: Answers include page numbers and sections
- ⚠️ **Safety Warnings**: Automatic warnings for safety-critical topics
- 🎯 **Confidence Scoring**: Answer confidence indicators
- 🌐 **REST API**: Full-featured FastAPI backend
- 🎨 **Web UI**: Beautiful Streamlit interface
- 🔧 **CLI Tools**: Command-line management utilities

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface                        │
│              (Streamlit / API Client)                    │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│                   FastAPI Backend                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Upload     │  │   Process    │  │    Query     │ │
│  │   Endpoint   │  │   Endpoint   │  │   Endpoint   │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└───────────────────────┬─────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   Document   │ │   Embedding  │ │  Similarity  │
│  Processing  │ │  Generation  │ │    Search    │
└──────────────┘ └──────────────┘ └──────────────┘
        │               │               │
        └───────────────┼───────────────┘
                        ▼
            ┌───────────────────────┐
            │  PostgreSQL + pgvector│
            │  (Chunks & Embeddings)│
            └───────────────────────┘
                        │
                        ▼
            ┌───────────────────────┐
            │    Google Gemini API  │
            │  (Embeddings & LLM)   │
            └───────────────────────┘
```

### Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Backend** | FastAPI | REST API endpoints |
| **Frontend** | Streamlit | User interface |
| **Database** | PostgreSQL 16 | Data storage |
| **Vector Search** | pgvector | Similarity search |
| **Embeddings** | Gemini text-embedding-004 | Text vectorization |
| **LLM** | Gemini 1.5 Pro | Answer generation |
| **PDF Processing** | PyMuPDF | Text extraction |
| **Containerization** | Docker & Docker Compose | Deployment |

## 📦 Prerequisites

### Required
- **Docker** & **Docker Compose** (v20.10+)
- **Python** 3.11+ (for local development)
- **Gemini API Key** from [Google AI Studio](https://makersuite.google.com/app/apikey)

### System Requirements
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 5GB free space
- **OS**: Linux, macOS, or Windows with WSL2

## 🚀 Installation

### 1. Clone Repository

```bash
git clone <your-repo-url>
cd car-manual-rag
```

### 2. Environment Setup

Create `.env` file:

```bash
cat > .env << EOF
# Gemini API
GEMINI_API_KEY=your_gemini_api_key_here

# Database Configuration
DB_HOST=postgres
DB_PORT=5432
DB_NAME=car_manual_db
DB_USER=rag_user
DB_PASSWORD=rag_password
EOF
```

**Get your Gemini API key:**
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy and paste into `.env` file

### 3. Install Dependencies

**Option A: Docker (Recommended)**

```bash
# No additional installation needed
docker-compose --version  # Verify Docker is installed
```

**Option B: Local Development**

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## 🎯 Quick Start

### Start the System

```bash
# Start all services (PostgreSQL + API)
python manage.py start

# Wait ~10 seconds for database to initialize

# Start Streamlit UI
python manage.py ui
```

**Access Points:**
- 🎨 **Streamlit UI**: http://localhost:8501
- 📚 **API Docs**: http://localhost:8000/docs
- 🏥 **Health Check**: http://localhost:8000/health

### Your First Query

#### Using Streamlit UI:

1. **Upload Manual**
   - Open http://localhost:8501
   - Go to "📚 Manage Manuals" tab
   - Upload your car manual PDF
   - System checks for duplicates automatically

2. **Process Manual**
   - Click "⚙️ Process" button
   - Wait for processing to complete (shown in status)
   - Processing extracts text, generates embeddings, stores in database

3. **Ask Questions**
   - Go to "💬 Chat" tab
   - Select your manual from dropdown
   - Type questions like:
     - "Berapa kapasitas mesin mobil ini?"
     - "Bagaimana cara mengganti oli?"
     - "Kapan harus servis rutin?"

#### Using CLI:

```bash
# Upload manual
python manage.py upload ./data/car_manual.pdf

# List manuals
python manage.py list

# Process manual (replace with your manual_id)
python manage.py process-manual manual_20250109_143022

# Check status
python manage.py process-status manual_20250109_143022

# Query via API
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Berapa kapasitas mesin?", "manual_id": "manual_20250109_143022"}'
```

## 📖 Usage

### Management Commands

```bash
# System Commands
python manage.py start              # Start all containers
python manage.py stop               # Stop all containers
python manage.py restart            # Restart containers
python manage.py status             # Show container status
python manage.py logs               # View logs
python manage.py clean              # Remove all data
python manage.py rebuild            # Rebuild from scratch

# API & UI
python manage.py api                # Start FastAPI server
python manage.py ui                 # Start Streamlit UI
python manage.py api-logs           # View API logs

# Manual Management
python manage.py upload <pdf>       # Upload manual
python manage.py list               # List all manuals
python manage.py process-manual <id> # Process manual
python manage.py process-status <id> # Check status

# Database
python manage.py db-shell           # Access PostgreSQL shell
```

### Streamlit UI Guide

#### 1. Chat Tab 💬
- **Select Manual**: Choose which manual to query
- **Ask Questions**: Type in natural language
- **View Answers**: Get AI-generated responses
- **Check Sources**: See page numbers and sections
- **Safety Warnings**: Automatic alerts for critical topics
- **Settings**: Adjust search parameters in sidebar

#### 2. Manage Manuals Tab 📚
- **Upload**: Drag & drop or browse PDF files
- **Duplicate Check**: Automatic hash-based detection
- **Process**: Extract text and generate embeddings
- **Monitor**: Check processing status
- **Delete**: Remove manuals (with confirmation)
- **View Stats**: See chunks and pages processed

#### 3. About Tab 📊
- System information
- Usage instructions
- Technology stack
- Tips for better results

### API Usage Examples

#### Upload Manual

```bash
curl -X POST http://localhost:8000/api/manuals/upload \
  -F "file=@car_manual.pdf"
```

**Response:**
```json
{
  "message": "Manual uploaded successfully",
  "manual_id": "manual_20250109_143022",
  "filename": "car_manual.pdf",
  "file_hash": "a3f2d8b...",
  "duplicate": false,
  "existing_manual_id": null
}
```

#### List Manuals

```bash
curl http://localhost:8000/api/manuals
```

#### Process Manual

```bash
curl -X POST "http://localhost:8000/api/manuals/manual_20250109_143022/process?start_page=0&process_images=false"
```

#### Query Manual

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Bagaimana cara mengganti oli mesin?",
    "manual_id": "manual_20250109_143022",
    "top_k": 5,
    "similarity_threshold": 0.5
  }'
```

**Response:**
```json
{
  "question": "Bagaimana cara mengganti oli mesin?",
  "answer": "Untuk mengganti oli mesin, ikuti langkah berikut...",
  "sources": [
    {
      "page": 45,
      "section": "BAB 3: Perawatan Rutin",
      "similarity": 0.89
    }
  ],
  "chunks_found": 3,
  "confidence": "High",
  "warning": null,
  "manual_id": "manual_20250109_143022"
}
```

## 📚 API Documentation

### Endpoints Overview

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/health` | GET | Health check |
| `/api/status` | GET | System statistics |
| `/api/manuals/upload` | POST | Upload PDF |
| `/api/manuals` | GET | List manuals |
| `/api/manuals/{id}` | GET | Get manual info |
| `/api/manuals/{id}` | DELETE | Delete manual |
| `/api/manuals/{id}/process` | POST | Process manual |
| `/api/manuals/{id}/process/status` | GET | Processing status |
| `/api/query` | POST | Query manual |
| `/api/query/filtered` | POST | Filtered query |
| `/api/chat` | POST | Multi-turn chat |

**Full API documentation**: http://localhost:8000/docs (when running)

## 📁 Project Structure

```
car-manual-rag/
│
├── core/                          # Database core
│   ├── db_connection.py          # Connection management
│   └── db_schema.py              # Schema creation
│
├── services/                      # RAG services
│   ├── embedding_generator.py    # Gemini embeddings
│   ├── similarity_search.py      # Vector search
│   ├── context_builder.py        # Context formatting
│   ├── answer_generator.py       # Answer generation
│   └── storage_manager.py        # Data storage
│
├── utils/                         # Utilities
│   ├── pdf_extractor.py          # PDF processing
│   ├── text_cleaner.py           # Text cleaning
│   └── text_chunker.py           # Text chunking
│
├── api/                           # FastAPI backend
│   └── main.py                   # API endpoints
│
├── ui/                            # Streamlit frontend
│   └── streamlit_app.py          # Web interface
│
├── scripts/                       # Utility scripts
│   └── process_document.py       # CLI processor
│
├── data/                          # Data storage
│   └── uploads/                  # Uploaded PDFs
│
├── rag_pipeline.py               # Main RAG logic
├── document_processor.py         # Document pipeline
├── manage.py                     # Management CLI
│
├── docker-compose.yml            # Docker setup
├── Dockerfile                    # Container config
├── requirements.txt              # Dependencies
├── .env                          # Environment vars
└── README.md                     # This file
```

### Key Files Explained

**Core Components:**
- `rag_pipeline.py`: Orchestrates the entire RAG workflow
- `document_processor.py`: Handles PDF processing pipeline
- `manage.py`: CLI tool for system management

**Services:**
- Each service is independent and testable
- Follow single responsibility principle
- Can be scaled horizontally if needed

**Data Flow:**
```
PDF → utils → services → core → PostgreSQL
Query → api → services → Gemini → Response
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `GEMINI_API_KEY` | Google Gemini API key | - | ✅ Yes |
| `DB_HOST` | PostgreSQL hostname | `postgres` | No |
| `DB_PORT` | PostgreSQL port | `5432` | No |
| `DB_NAME` | Database name | `car_manual_db` | No |
| `DB_USER` | Database user | `rag_user` | No |
| `DB_PASSWORD` | Database password | `rag_password` | No |

### Query Parameters

Adjust these for better results:

| Parameter | Description | Range | Default |
|-----------|-------------|-------|---------|
| `top_k` | Number of chunks to retrieve | 1-20 | 5 |
| `similarity_threshold` | Minimum similarity score | 0.0-1.0 | 0.5 |
| `chunk_size` | Characters per chunk | 500-2000 | 800 |
| `chunk_overlap` | Overlap between chunks | 50-500 | 150 |

**Tuning Tips:**
- **Low relevance?** → Increase `top_k` or lower `similarity_threshold`
- **Too much irrelevant info?** → Decrease `top_k` or raise `similarity_threshold`
- **Missing context?** → Increase `chunk_size` and `chunk_overlap`

## 🧪 Testing

### Run Tests

```bash
# All tests
pytest -v

# Specific test file
pytest tests/test_rag_pipeline.py -v -s

# With coverage
pytest --cov=. --cov-report=html
```

### Manual Testing

```bash
# 1. Upload test manual
python manage.py upload ./data/test_manual.pdf

# 2. Process it
python manage.py process-manual <manual_id>

# 3. Test query
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "test question", "manual_id": "<manual_id>"}'
```

### Health Checks

```bash
# API health
curl http://localhost:8000/health

# Database health
docker-compose exec postgres pg_isready -U rag_user

# Check logs
python manage.py logs
```

## 🔧 Troubleshooting

### Common Issues

#### 1. API Not Starting

**Symptom:** `Connection refused` or `API not running`

**Solutions:**
```bash
# Check if containers are running
docker-compose ps

# View logs
python manage.py logs

# Restart services
python manage.py restart

# If still failing, rebuild
python manage.py rebuild
```

#### 2. Database Connection Error

**Symptom:** `password authentication failed` or `connection refused`

**Solutions:**
```bash
# Stop all containers
docker-compose down

# Remove volumes (WARNING: deletes all data)
docker-compose down -v

# Start fresh
python manage.py start
```

#### 3. Upload Fails

**Symptom:** Upload returns error

**Solutions:**
- Check file is valid PDF
- Ensure file size < 100MB
- Verify `data/uploads/` directory exists
- Check API logs: `python manage.py api-logs`

#### 4. Processing Stuck

**Symptom:** Processing never completes

**Solutions:**
```bash
# Check processing status
python manage.py process-status <manual_id>

# View detailed logs
python manage.py api-logs

# Check Gemini API quota
# Visit: https://makersuite.google.com/app/apikey
```

#### 5. No Relevant Results

**Symptom:** "No information available" for valid questions

**Solutions:**
- Lower similarity threshold (try 0.3-0.4)
- Increase top_k (try 8-10)
- Verify manual was processed correctly
- Check if question is in Bahasa Indonesia
- Ensure relevant content exists in manual

#### 6. Out of Memory

**Symptom:** Container crashes or system freezes

**Solutions:**
- Increase Docker memory limit (Settings → Resources)
- Process documents in batches (use `end_page` parameter)
- Close other applications
- Use smaller chunk sizes

### Debug Mode

Enable detailed logging:

```bash
# Set in .env
LOG_LEVEL=DEBUG

# Restart services
python manage.py restart

# View detailed logs
python manage.py logs
```

### Get Help

1. Check logs: `python manage.py logs`
2. Verify configuration: Check `.env` file
3. Test API health: `curl http://localhost:8000/health`
4. Check database: `python manage.py db-shell`

## 🤝 Contributing

Contributions are welcome! Here's how:

### Development Setup

```bash
# 1. Fork and clone
git clone <your-fork>
cd car-manual-rag

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install dev dependencies
pip install pytest pytest-cov black flake8

# 5. Create feature branch
git checkout -b feature/your-feature

# 6. Make changes and test
pytest -v

# 7. Format code
black .

# 8. Commit and push
git commit -m "Add your feature"
git push origin feature/your-feature

# 9. Create Pull Request
```

### Code Style

- Follow PEP 8
- Use type hints
- Write docstrings
- Add tests for new features
- Keep functions focused (single responsibility)

### Testing Guidelines

- Write tests for new features
- Maintain >80% coverage
- Test edge cases
- Mock external APIs (Gemini)

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

## 🙏 Acknowledgments

- **Google Gemini** for embeddings and LLM
- **pgvector** for vector similarity search
- **FastAPI** for API framework
- **Streamlit** for UI framework
- **PyMuPDF** for PDF processing

## 📞 Support

- 📖 **Documentation**: This README
- 💬 **Issues**: [GitHub Issues](your-repo-url/issues)
- 📧 **Email**: your-email@example.com

## 🗺️ Roadmap

### Coming Soon
- [ ] Multi-language support (English, etc.)
- [ ] Image understanding (diagrams, charts)
- [ ] Voice input/output
- [ ] Conversation history persistence
- [ ] User authentication
- [ ] Advanced analytics dashboard
- [ ] Export Q&A to PDF
- [ ] Mobile app

### Under Consideration
- [ ] Support for other document types (DOCX, HTML)
- [ ] Integration with automotive APIs
- [ ] Batch processing multiple manuals
- [ ] Fine-tuned models for automotive domain
- [ ] Cloud deployment guides (AWS, GCP, Azure)

## 📊 Performance

### Benchmarks

| Operation | Time | Notes |
|-----------|------|-------|
| Upload (50MB PDF) | ~5s | Network dependent |
| Process (100 pages) | ~3-5min | Gemini API rate limited |
| Query (single) | ~2-3s | Including LLM generation |
| Similarity Search | <100ms | Vector search only |

### Optimization Tips

1. **Batch Processing**: Process multiple pages simultaneously
2. **Caching**: Results are not cached (implement Redis for production)
3. **Indexing**: pgvector HNSW index for faster search
4. **Chunking**: Optimize chunk size for your use case

---

## 🎉 Quick Reference Card

```bash
# Start System
python manage.py start && python manage.py api && python manage.py ui

# Upload & Process
python manage.py upload manual.pdf
python manage.py process-manual <id>

# Access
🎨 UI:   http://localhost:8501
📚 Docs: http://localhost:8000/docs

# Stop System
python manage.py stop

# Clean Everything
python manage.py clean
```

---

**Built with ❤️ for automotive enthusiasts and developers**

**Version**: 1.0.0  
**Last Updated**: January 2025