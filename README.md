# Reviews Copilot

Multi-location business review management system with AI-powered sentiment analysis, topic extraction, and reply suggestions.

## Tech Stack

### Backend (Python)
- **FastAPI** 0.104.1 - Modern async web framework with automatic OpenAPI docs
- **SQLModel** 0.0.14 - Type-safe SQL database interactions (Pydantic + SQLAlchemy)
- **Uvicorn** 0.22.0 - ASGI server with hot reload
- **Pydantic** 2.1.1 - Data validation and serialization
- **Python-dotenv** 1.0.0 - Environment variable management

### Database & Storage
- **PostgreSQL** 15-alpine - Production database with connection pooling
- **SQLite** - Development/fallback database
- **psycopg2-binary** 2.9.9 - PostgreSQL adapter for Python

### AI & Machine Learning
- **OpenAI API** 1.3.0 - GPT-3.5-turbo for primary AI features
- **HuggingFace Transformers** 4.38.0 - Local AI fallback models:
  - `distilbert-base-uncased-finetuned-sst-2-english` (66M params) - Sentiment analysis
  - `facebook/bart-large-mnli` (400M params) - Zero-shot topic classification  
  - `microsoft/DialoGPT-small` (117M params) - Conversational reply generation
- **PyTorch** 2.0.0+ - Deep learning framework for transformers
- **scikit-learn** 1.3.2 - TF-IDF vectorization and cosine similarity search

### Caching & Rate Limiting
- **Redis** 5.0.1 - In-memory caching and session storage
- **slowapi** 0.1.9 - Rate limiting with Redis backend

### Frontend (React + TypeScript)
- **React** 18+ - Modern UI library with hooks
- **TypeScript** 5+ - Type-safe JavaScript development
- **Vite** 4+ - Fast build tool and dev server
- **React Router** 6+ - Client-side routing
- **Recharts** 2+ - Interactive data visualization charts

### Testing & Development
- **pytest** 7.4.0 - Python testing framework
- **httpx** 0.24.1 - Async HTTP client for testing
- **ESLint + Prettier** - Code linting and formatting

### DevOps & Deployment
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Nginx** - Reverse proxy and SSL termination
- **DuckDNS** - Dynamic DNS service
- **AWS EC2** - Cloud hosting

########################################### setup ######################################

### Prerequisites
- Python 3.9+
- Node.js 18+
- Docker & Docker Compose
########################################################################################







############################## .env sample ###########################################

Create `backend/.env`:
```bash
# Database (choose one)
DATABASE_URL=sqlite:///./data.db
# DATABASE_URL=postgresql://user:password@localhost:5432/reviews_db (recommended)

# AI Configuration  
OPENAI_API_KEY=your_openai_api_key_here

# API Security
API_KEY=supersecret

# Optional: Redis for caching/rate limiting
REDIS_URL=redis://localhost:6379

# CORS Origins (comma-separated)
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```
########################################################################################





############################### Quick Start ##########################################

# Using Docker (recommended)
docker-compose up --build

# Manual setup  
cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload
cd frontend && npm install && npm run dev

API Documentation: http://localhost:8000/docs
#########################################################################################





##################################### how to run tests ##################################

```bash
# Backend tests
cd backend
python -m pytest -v

# Specific test file
python -m pytest app/tests/test_ingest.py -v
```

## how you deployed

### Local Development
```bash
# Using Docker (recommended)
docker-compose up --build

# Manual setup
cd backend && python -m uvicorn app.main:app --reload
cd frontend && npm run dev
```
#########################################################################################






######################### Production Deployment #########################################

Took a subdomain(autoreview.duckdns.org) from duckdns.org - pointed to ->  my ec2 IP
Nginx reverse proxy to -> localhost:3000 ( exposed as 3001 with docker 3000)
with proper SSL handling for 443 traffic HTTPS support

Backend is not exposed and was handled internally reverse proxy /api/<endpoint>

################################################################################



######################## time spent & trade-offs ######################################

1. day1 : did a thorough research and created implementation plan
2. day2 : project scaffolded with starter code
3. day3 : full implementation with proper docker setup
4. day4 : deployment and post documentation

###########################################################





########################### What I'd Do With More Time #############################
- Add OAuth2/JWT authentication
- Implement comprehensive input validation
- Add E2E testing with Playwright  
- Create advanced analytics dashboards
- Add real-time WebSocket updates
- Implement background job processing
- parallel processing
###########################################################################
