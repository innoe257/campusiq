# CampusIQ

<p align="center">
  <strong>AI-Powered Student Success Platform for Higher Education</strong>
</p>

<p align="center">
  <a href="#architecture">Architecture</a> •
  <a href="#tech-stack">Tech Stack</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#features">Features</a> •
  <a href="#deployment">Deployment</a>
</p>

<p align="center">
  <a href="https://render.com/deploy?repo=https://github.com/innoe257/campusiq">
    <img src="https://render.com/images/deploy-to-render-button.svg" alt="Deploy to Render" />
  </a>
</p>

---

## Overview

**CampusIQ** is a full-stack, open-source platform designed to improve student retention and success in higher education. It combines traditional machine learning (predictive analytics) with modern generative AI (RAG-powered academic advisor) to provide faculty and students with actionable insights.

This project demonstrates end-to-end software engineering and AI/ML skills aligned with the New Zealand tech market — including FastAPI, PostgreSQL/pgvector, Next.js, LangChain, XGBoost, MLflow, Airflow, Docker, and AWS-ready Terraform infrastructure.

---

## Features

| Feature | Description | Technology |
|---------|-------------|------------|
| **Predictive Early Alert** | ML model identifies at-risk students using academic and engagement data | XGBoost, MLflow, scikit-learn |
| **AI Academic Advisor** | RAG chatbot answers questions from official university documents | LangChain, Ollama (local LLM), pgvector |
| **Faculty Dashboard** | Real-time analytics, risk distribution, and intervention queue | Next.js, Recharts, FastAPI |
| **Student Directory** | Searchable directory with risk scores and academic standing | PostgreSQL, SQLAlchemy |
| **Data Pipeline** | Automated ETL with synthetic data generation and quality tests | Apache Airflow, dbt |
| **MLOps** | Experiment tracking, model versioning, and automated retraining | MLflow, DVC, GitHub Actions |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CampusIQ Architecture                     │
├─────────────────────────────────────────────────────────────────┤
│  Frontend (Next.js 14)                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │  Dashboard  │  │  AI Advisor │  │    Student Directory    │  │
│  │  (Charts)   │  │  (Chat UI)  │  │    (Search/Filter)      │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
│                           │                                     │
│                           ▼                                     │
│                  FastAPI Backend (Python)                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │ Auth/JWT    │  │ Predictions │  │      RAG Service        │  │
│  │  OAuth2     │  │   XGBoost   │  │  LangChain + Ollama     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
│                           │                                     │
│           ┌───────────────┼───────────────┐                     │
│           ▼               ▼               ▼                     │
│    ┌──────────┐    ┌──────────┐    ┌──────────────┐            │
│    │PostgreSQL│    │  Redis   │    │   MLflow     │            │
│    │ +pgvector│    │ (Cache)  │    │ (Tracking)   │            │
│    └──────────┘    └──────────┘    └──────────────┘            │
│                                                                 │
│  Data Pipeline (Airflow)     ML Training                        │
│  ┌────────────┐             ┌────────────┐                     │
│  │ Synthetic  │             │  XGBoost   │                     │
│  │ Data Gen   │ ──▶ dbt ──▶ │   Model    │                     │
│  └────────────┘             └────────────┘                     │
└─────────────────────────────────────────────────────────────────┘
```

See [docs/architecture.md](docs/architecture.md) for detailed C4 diagrams and data flow.

---

## Tech Stack

### Backend
- **FastAPI** — Modern, high-performance Python web framework
- **SQLAlchemy + PostgreSQL** — ORM and relational database
- **pgvector** — Vector similarity search for RAG
- **LangChain** — LLM orchestration and RAG pipeline
- **Ollama** — Local LLM inference (Llama2/Mistral)
- **Redis** — Caching and session storage

### AI/ML
- **XGBoost** — Gradient boosting for attrition prediction
- **scikit-learn** — Feature engineering and preprocessing
- **MLflow** — Experiment tracking and model registry
- **DVC** — Data and model versioning
- **sentence-transformers** — Open-source embeddings

### Frontend
- **Next.js 14** — React framework with App Router
- **TypeScript** — Type-safe development
- **Tailwind CSS** — Utility-first styling
- **Recharts** — Data visualization
- **Lucide React** — Icon library

### Data Engineering
- **Apache Airflow** — Workflow orchestration
- **dbt** — Data transformations and testing
- **Pandas / NumPy** — Data manipulation

### DevOps & Infrastructure
- **Docker + Docker Compose** — Containerization
- **Terraform** — Infrastructure as Code (AWS-ready)
- **GitHub Actions** — CI/CD pipelines
- **Prometheus + Grafana** — Monitoring (local)

---

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Git
- 8GB+ RAM (for Ollama local LLM)

### 1. Clone the Repository

```bash
git clone https://github.com/innocentmamvura/campusiq.git
cd campusiq
```

### 2. Start All Services

```bash
docker-compose up -d
```

This will start:
- PostgreSQL with pgvector (port 5432)
- Redis (port 6379)
- Ollama for local LLMs (port 11434)
- MLflow UI (port 5000)
- Airflow Web UI (port 8080)
- FastAPI Backend (port 8000)
- Next.js Frontend (port 3000)

### 3. Pull the LLM Model

```bash
docker exec -it campusiq-ollama ollama pull llama2
```

> Note: The first pull downloads ~3.8GB. You can also use `mistral` or `phi` for smaller models.

### 4. Ingest Knowledge Documents

```bash
curl -X POST http://localhost:8000/api/v1/chat/ingest \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Or use the API docs at [http://localhost:8000/docs](http://localhost:8000/docs)

### 5. Access the Application

| Service | URL | Default Credentials |
|---------|-----|---------------------|
| Frontend | http://localhost:3000 | — |
| API Docs | http://localhost:8000/docs | — |
| Airflow | http://localhost:8080 | admin / admin |
| MLflow | http://localhost:5000 | — |

---

## Project Structure

```
campusiq/
├── .github/workflows/          # CI/CD pipelines
├── backend/                    # FastAPI application
│   ├── app/
│   │   ├── api/v1/            # API routes (auth, students, predictions, chat)
│   │   ├── core/              # Config and security
│   │   ├── db/                # Database session and vector store init
│   │   ├── models/            # SQLAlchemy models
│   │   ├── services/          # Business logic (RAG, predictions)
│   │   └── main.py            # FastAPI entry point
│   ├── tests/                 # Pytest test suite
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                   # Next.js application
│   ├── app/                   # Pages (dashboard, advisor, students)
│   ├── components/            # Reusable UI components
│   ├── lib/                   # API client utilities
│   ├── tests/e2e/             # Playwright E2E tests
│   ├── Dockerfile
│   └── package.json
├── data_pipeline/              # Airflow DAGs and dbt models
│   ├── dags/                  # Airflow workflow definitions
│   └── dbt/                   # Data transformations
├── ml/                         # Machine learning pipeline
│   └── models/                # Training scripts and saved models
├── knowledge_base/             # Documents for RAG ingestion
├── infrastructure/             # Terraform AWS infrastructure
│   └── terraform/
├── notebooks/                  # Jupyter notebooks for EDA
├── docs/                       # Technical documentation
├── docker-compose.yml          # Local development stack
├── dvc.yaml                    # DVC pipeline definition
└── README.md                   # This file
```

---

## Key Workflows

### Running the ML Pipeline

```bash
# Generate synthetic data
python data_pipeline/data_generator.py

# Run model training with MLflow tracking
python ml/models/train.py

# Or use DVC for reproducible pipelines
dvc repro
```

### Running Data Quality Tests

```bash
cd data_pipeline/dbt
dbt test
```

### Running Backend Tests

```bash
cd backend
pytest tests/ -v
```

### Running Frontend E2E Tests

```bash
cd frontend
npm run test:e2e
```

---

## Deployment

### AWS Deployment (via Terraform)

1. Configure AWS credentials
2. Update `infrastructure/terraform/terraform.tfvars` with your settings
3. Deploy:

```bash
cd infrastructure/terraform
terraform init
terraform plan
terraform apply
```

This provisions:
- VPC with public/private subnets
- ECS Fargate cluster for containers
- RDS PostgreSQL with pgvector
- Application Load Balancer
- ECR repositories for Docker images

### Render Deployment (Free Live URL)

The fastest way to get a live URL for employers is deploying to **Render**.

#### Option 1: One-Click Deploy (Recommended)

Click the button below and Render will automatically:
- Create a PostgreSQL database
- Deploy the FastAPI backend
- Deploy the Next.js frontend as a static site
- Generate environment variables
- Run database migrations and seed sample data

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/innoe257/campusiq)

#### Option 2: Manual Deploy

1. **Create a Render account** at [render.com](https://render.com) (free, no credit card)

2. **Create a PostgreSQL database**:
   - Dashboard → New → PostgreSQL
   - Name: `campusiq-db`
   - Region: Oregon (US West) or Singapore (Asia)
   - Plan: Free

3. **Deploy the Backend**:
   - Dashboard → New → Web Service
   - Connect your GitHub repo `innoe257/campusiq`
   - Name: `campusiq-backend`
   - Environment: Python 3
   - Build Command: `cd backend && pip install -r requirements.txt`
   - Start Command: `cd backend && bash render-start.sh`
   - Add environment variables:
     - `DATABASE_URL` → copy from your PostgreSQL "Internal Database URL"
     - `SECRET_KEY` → generate a random string
     - `FRONTEND_URL` → `https://campusiq-frontend.onrender.com`
     - `RENDER` → `true`

4. **Deploy the Frontend**:
   - Dashboard → New → Static Site
   - Connect the same repo
   - Name: `campusiq-frontend`
   - Build Command: `cd frontend && npm install && npm run build`
   - Publish Directory: `frontend/out`
   - Add environment variable:
     - `NEXT_PUBLIC_API_URL` → `https://campusiq-backend.onrender.com`

5. **Update CORS** (if needed):
   - After frontend deploys, copy its URL
   - Add it to the backend's `FRONTEND_URL` environment variable
   - Redeploy backend

#### What Works on Render Free Tier

| Feature | Status | Notes |
|---------|--------|-------|
| Faculty Dashboard | ✅ Live | Full interactive charts |
| Student Directory | ✅ Live | Search, filter, risk scores |
| AI Chat Advisor | ✅ Live | Intelligent demo responses |
| Authentication | ✅ Live | JWT login/register |
| Predictions API | ✅ Live | Rule-based risk scoring |
| RAG (Vector Search) | ⚠️ Demo Mode | No pgvector on free PostgreSQL |
| Ollama LLM | ❌ Not Available | No GPU on free tier |
| MLflow UI | ❌ Not Available | Replaced with SQLite backend |
| Airflow | ❌ Not Available | ETL not scheduled |

> **Note:** Free tier web services "sleep" after 15 minutes of inactivity. The first request after sleep takes ~30 seconds to wake up. For interviews, wake the service beforehand by visiting the URL.

---

### CI/CD

GitHub Actions automatically:
- Runs backend tests (Pytest)
- Runs frontend tests (Lint + Build)
- Tests ML pipeline (Data generation + Model training)
- Builds Docker images
- Validates Terraform
- Deploys to AWS ECS on merges to `main`

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+psycopg2://campusiq:campusiq_dev_password@localhost:5432/campusiq` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `OLLAMA_HOST` | Ollama API endpoint | `http://localhost:11434` |
| `MLFLOW_TRACKING_URI` | MLflow tracking server | `http://localhost:5000` |
| `SECRET_KEY` | JWT signing key | (dev default — change in prod) |

See `.env.example` for a complete list.

---

## Contributing

This is a portfolio project, but contributions are welcome:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

---

## Acknowledgments

- Built for the NZ tech job market — targeting AI/ML Engineering and Full-Stack roles
- Uses 100% open-source tools (no paid API keys required for local development)
- Inspired by real student success platforms used in higher education

---

## Contact

**Innocent Mamvura**
- GitHub: [@innocentmamvura](https://github.com/innocentmamvura)
- LinkedIn: [linkedin.com/in/innocentmamvura](https://linkedin.com/in/innocentmamvura)

---

<p align="center">
  Built with passion for AI/ML and higher education technology
</p>
