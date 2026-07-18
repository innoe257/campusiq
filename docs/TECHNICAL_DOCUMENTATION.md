# CampusIQ Technical Documentation

**Version:** 0.1.0  
**Date:** January 2026  
**Author:** Innocent Mamvura  

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Problem Statement](#problem-statement)
3. [System Architecture](#system-architecture)
4. [Technology Rationale](#technology-rationale)
5. [Data Model](#data-model)
6. [AI/ML Pipeline](#aiml-pipeline)
7. [RAG Implementation](#rag-implementation)
8. [Security](#security)
9. [Deployment Strategy](#deployment-strategy)
10. [Monitoring & Observability](#monitoring--observability)
11. [Future Enhancements](#future-enhancements)

---

## Executive Summary

CampusIQ is an AI-powered student success platform built to demonstrate end-to-end software engineering and machine learning capabilities. The system addresses a real-world problem in higher education: student attrition. By combining predictive analytics with generative AI, CampusIQ provides institutions with early warning systems and students with intelligent academic support.

**Key Metrics Targeted:**
- Reduce student attrition by 15-20% through early identification
- Decrease advisor workload by 40% through AI-powered first-line support
- Improve course completion rates through personalized study planning

---

## Problem Statement

### Context
Universities worldwide face a student attrition crisis. In New Zealand, approximately 20% of first-year students do not continue to their second year. Traditional early alert systems rely on manual grade checks and advisor intuition, which are reactive rather than proactive.

### Challenges
1. **Scale**: Faculty advisors manage 500+ students each; personalized attention is impossible
2. **Data Silos**: Academic, financial, and engagement data live in separate systems
3. **Reactive Support**: Interventions happen after problems are visible, not before
4. **24/7 Needs**: Students need support outside business hours
5. **Resource Constraints**: Counseling and tutoring services are overwhelmed

### Solution
CampusIQ provides:
1. **Predictive Early Alerts**: ML models identify at-risk students 3 months before visible failure
2. **AI Academic Advisor**: RAG-powered chatbot provides instant, accurate answers from official documents
3. **Faculty Dashboard**: Unified view of cohort health with prioritized intervention queue
4. **Automated Workflows**: Data pipelines keep models current without manual intervention

---

## System Architecture

### High-Level Design

```
┌─────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │   Web App    │  │  Mobile Web  │  │     API Consumers        │  │
│  │  (Next.js)   │  │  (Responsive)│  │  (Third-party systems)   │  │
│  └──────────────┘  └──────────────┘  └──────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                             API GATEWAY                              │
│                    FastAPI (Python 3.11, Async)                      │
│  ┌─────────────┐  ┌─────────────┐  ┌────────────────────────────┐  │
│  │   Router    │  │   Auth      │  │    Rate Limiting (Redis)   │  │
│  │             │  │  (JWT/OAuth)│  │                            │  │
│  └─────────────┘  └─────────────┘  └────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                    │
            ┌───────────────────────┼───────────────────────┐
            ▼                       ▼                       ▼
┌─────────────────┐     ┌─────────────────┐     ┌──────────────────┐
│  PREDICTION     │     │      RAG        │     │   STUDENT MGMT   │
│   SERVICE       │     │    SERVICE      │     │     SERVICE      │
│  (XGBoost ML)   │     │ (LangChain +    │     │  (CRUD + Search) │
│                 │     │   Ollama LLM)   │     │                  │
└─────────────────┘     └─────────────────┘     └──────────────────┘
            │                       │                       │
            └───────────────────────┼───────────────────────┘
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                           DATA LAYER                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │  PostgreSQL  │  │   pgvector   │  │        Redis Cache       │  │
│  │  (Relational)│  │  (Embeddings)│  │   (Sessions + Rate Lim)  │  │
│  └──────────────┘  └──────────────┘  └──────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                    │
            ┌───────────────────────┼───────────────────────┐
            ▼                       ▼                       ▼
┌─────────────────┐     ┌─────────────────┐     ┌──────────────────┐
│  DATA PIPELINE  │     │  ML PIPELINE    │     │  MONITORING      │
│  (Airflow + dbt)│     │ (MLflow + DVC)  │     │ (Prom + Grafana) │
└─────────────────┘     └─────────────────┘     └──────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Scaling Strategy |
|-----------|---------------|------------------|
| Next.js Frontend | SSR React app, dashboards, chat UI | Static + CDN |
| FastAPI Backend | API routing, business logic, orchestration | Horizontal (ECS) |
| PostgreSQL | Transactional data, vector search | Vertical (RDS) |
| Redis | Session cache, rate limiting | Redis Cluster |
| Ollama | Local LLM inference | Dedicated GPU instance |
| Airflow | ETL scheduling, data quality | Single node (local dev) |
| MLflow | Experiment tracking, model registry | Single node |

---

## Technology Rationale

### Why FastAPI?
- Native async support for concurrent ML model calls
- Automatic OpenAPI documentation generation
- Pydantic integration for request/response validation
- Python ecosystem alignment for ML/AI code

### Why PostgreSQL + pgvector?
- Single database for relational + vector data reduces operational complexity
- pgvector is production-ready and supports HNSW indexing
- ACID compliance for student data (financial aid, grades)
- AWS RDS supports pgvector natively

### Why Ollama (Local LLM)?
- Zero API costs for development and small-scale deployment
- Data privacy — student queries never leave the infrastructure
- No vendor lock-in to OpenAI/Anthropic
- NZ employers value cost-effective, self-hosted AI solutions

### Why XGBoost over Deep Learning?
- Interpretable predictions (SHAP values for feature importance)
- Faster training and inference
- Better performance on tabular data with < 100k samples
- Easier to maintain and debug in production

### Why LangChain for RAG?
- Abstracts vector store operations
- Built-in conversation memory
- Modular component architecture
- Active community and documentation

---

## Data Model

### Entity Relationship Diagram

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│    User     │       │   Student   │       │   Course    │
├─────────────┤       ├─────────────┤       ├─────────────┤
│ id (PK)     │       │ id (PK)     │       │ id (PK)     │
│ username    │       │ student_id  │       │ course_code │
│ email       │       │ first_name  │       │ title       │
│ role        │       │ last_name   │       │ credits     │
│ hashed_pass │       │ program     │       │ program     │
└─────────────┘       │ gpa         │       │ difficulty  │
                      │ credits_... │       └─────────────┘
                      └─────────────┘
                            │
                            │ 1:N
                            ▼
                      ┌─────────────┐
                      │  Prediction │
                      ├─────────────┤
                      │ id (PK)     │
                      │ student_id  │
                      │ risk_score  │
                      │ risk_cat    │
                      │ top_factors │
                      │ model_ver   │
                      └─────────────┘
                            │
                            │ 1:N
                            ▼
                      ┌─────────────┐
                      │  StudyPlan  │
                      ├─────────────┤
                      │ id (PK)     │
                      │ student_id  │
                      │ plan_data   │
                      └─────────────┘
```

### Key Design Decisions
1. **Separate User and Student tables**: Allows faculty/advisors to log in without being students
2. **JSON columns for factors and plans**: Flexible schema for evolving ML features
3. **Soft deletes (is_active)**: Preserves data history for audit and retraining
4. **Timestamp columns**: Enables time-series analysis and model drift detection

---

## AI/ML Pipeline

### Attrition Prediction Model

**Problem Type:** Binary classification (dropout vs. continue)  
**Algorithm:** XGBoost with hyperparameter tuning  
**Input Features:**
| Feature | Type | Description |
|---------|------|-------------|
| current_gpa | float | Current semester GPA |
| attendance_rate | float | Percentage of classes attended |
| engagement_score | float | LMS login frequency, assignment submission rate |
| credits_earned | int | Total credits completed |
| credits_attempted | int | Total credits enrolled |
| financial_aid | bool | Receives financial assistance |
| first_generation | bool | First in family to attend college |
| credit_completion_rate | float | credits_earned / credits_attempted |
| gpa_trend | float | current_gpa - first_semester_gpa |
| years_enrolled | int | Current year - enrollment_year |

**Engineered Features:**
- `gpa_x_attendance`: Interaction between academic performance and presence
- `engagement_x_completion`: Interaction between engagement and success rate

**Model Performance Targets:**
- AUC-ROC: > 0.80
- Precision (at-risk): > 0.70
- Recall (at-risk): > 0.75

**MLOps Workflow:**
```
Raw Data → ETL (Airflow) → Feature Store → Train (MLflow) → Evaluate → Register → Deploy
                                    ↑                                              │
                                    └────────────── Monitor Drift ←────────────────┘
```

### Experiment Tracking
MLflow logs:
- Hyperparameters
- Cross-validation metrics
- Feature importances
- Model artifacts (pickled model + scaler)
- Training dataset version (via DVC)

---

## RAG Implementation

### Architecture
```
User Query → Embed (MiniLM) → Vector Search (pgvector) → Retrieve Top-K → 
Build Prompt (Context + Query) → LLM (Ollama/Llama2) → Streaming Response
```

### Document Processing Pipeline
1. **Load**: Markdown files from `knowledge_base/`
2. **Chunk**: RecursiveCharacterTextSplitter (500 chars, 50 overlap)
3. **Embed**: `sentence-transformers/all-MiniLM-L6-v2` (384-dim)
4. **Store**: pgvector with cosine similarity index (IVFFlat, 100 lists)
5. **Query**: Cosine similarity search with 0.3 threshold

### Guardrails
- **PII Filtering**: No student-specific data in RAG context
- **Topic Guard**: Rejects off-topic queries (only academic/career)
- **Source Attribution**: Every response includes referenced document IDs
- **Confidence Threshold**: Returns "I don't know" if max similarity < 0.3

### Prompt Engineering
```
You are CampusIQ, an AI academic advisor for a university.
Answer the student's question based ONLY on the provided context.
If the answer isn't in the context, say so clearly.
Be concise, accurate, and helpful.

Context:
{retrieved_documents}

Question: {user_query}

Answer:
```

---

## Security

### Authentication
- OAuth2 Password Bearer flow with JWT tokens
- Token expiry: 30 minutes
- Password hashing: bcrypt with salt

### Authorization
- Role-based access control (student, faculty, admin)
- Faculty can view all students; students can only view their own data
- Admin access for ingestion and model management

### Data Protection
- PostgreSQL SSL connections in production
- Environment variables for secrets (no hardcoded credentials)
- Input validation via Pydantic models
- SQL injection prevention via SQLAlchemy parameterized queries

### Rate Limiting
- Redis-backed rate limiting on chat endpoints
- Prevents LLM abuse and ensures fair resource allocation

---

## Deployment Strategy

### Local Development
- Docker Compose with all services
- Hot reload for backend (uvicorn --reload)
- Hot reload for frontend (next dev)
- MLflow and Airflow accessible locally

### AWS Production (via Terraform)

**Infrastructure:**
- **Region**: ap-southeast-2 (Sydney, nearest to NZ)
- **Compute**: ECS Fargate (serverless containers)
- **Database**: RDS PostgreSQL 15 with pgvector extension
- **Load Balancer**: Application Load Balancer with health checks
- **Storage**: S3 for MLflow artifacts and document backups
- **Networking**: VPC with public/private subnets, NAT Gateway

**Deployment Flow:**
```
Git Push → GitHub Actions → Test → Build Docker → Push ECR → 
Terraform Plan → ECS Deploy → Health Check → Route Traffic
```

**Cost Optimization:**
- FARGATE_SPOT for non-critical workloads
- RDS reserved instances for predictable costs
- Ollama on EC2 Spot with GPU (g4dn.xlarge) for inference

---

## Monitoring & Observability

### Metrics (Prometheus)
- API request latency and throughput
- LLM inference time
- Model prediction latency
- Database query performance
- Cache hit/miss ratios

### Dashboards (Grafana)
- System health overview
- API endpoint performance
- Model drift indicators
- RAG retrieval accuracy
- Student risk trend over time

### Alerts
- Model accuracy drop > 10%
- LLM service down > 5 minutes
- Database connection failures
- High error rate (> 5% of requests)

---

## Future Enhancements

### Phase 2 (3 months)
- [ ] Real-time streaming data (Kafka) for live engagement metrics
- [ ] Multi-modal RAG (PDF syllabus parsing with OCR)
- [ ] A/B testing framework for model variants
- [ ] Mobile app (React Native)

### Phase 3 (6 months)
- [ ] Federated learning for multi-institution collaboration
- [ ] Explainable AI dashboard (SHAP visualizations)
- [ ] Integration with LMS platforms (Canvas, Moodle, Blackboard)
- [ ] Automated intervention workflows (email, SMS, calendar invites)

### Research Directions
- [ ] Causal inference for intervention effectiveness
- [ ] Fairness auditing across demographic groups
- [ ] Reinforcement learning for personalized study schedules
- [ ] Multilingual support (Māori, Samoan, Mandarin)

---

## Appendix A: API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | /api/v1/auth/register | Create new account | No |
| POST | /api/v1/auth/login | Obtain JWT token | No |
| GET | /api/v1/auth/me | Get current user | Yes |
| GET | /api/v1/students | List students | Yes |
| GET | /api/v1/students/dashboard/stats | Dashboard metrics | Yes |
| GET | /api/v1/students/{id} | Student detail | Yes |
| POST | /api/v1/predictions/predict/{id} | Predict risk | Yes |
| POST | /api/v1/chat/message | Chat with advisor | Yes |
| POST | /api/v1/chat/ingest | Ingest documents | Admin |

## Appendix B: Local Development Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Run migrations manually
docker exec campusiq-backend python -m app.db.init_vector_store

# Pull LLM model
docker exec -it campusiq-ollama ollama pull llama2

# Run tests
docker exec campusiq-backend pytest tests/ -v
docker exec campusiq-frontend npm test

# Access Airflow
curl -u admin:admin http://localhost:8080/api/v1/dags
```

## Appendix C: Troubleshooting

| Issue | Solution |
|-------|----------|
| Ollama connection refused | Ensure container is running: `docker-compose ps ollama` |
| Vector search returns nothing | Run ingestion: `POST /api/v1/chat/ingest` |
| Database connection errors | Wait for postgres healthcheck: `docker-compose logs postgres` |
| MLflow UI not loading | Check MLflow container: `docker-compose logs mlflow` |
| Frontend API errors | Verify `NEXT_PUBLIC_API_URL` in docker-compose.yml |

---

**Document Version Control**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1.0 | 2026-01-15 | Innocent Mamvura | Initial documentation |
