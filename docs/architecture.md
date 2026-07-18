# CampusIQ Architecture

## C4 Model

### Level 1: System Context

```
┌─────────────────────────────────────────────────────────────────┐
│                         CampusIQ System                          │
│                                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ Students │  │ Faculty  │  │ Advisors │  │  Admin   │       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
│       │             │             │             │              │
│       └─────────────┴─────────────┴─────────────┘              │
│                         │                                       │
│                         ▼                                       │
│              ┌─────────────────────┐                           │
│              │     CampusIQ        │                           │
│              │  (Web Application)  │                           │
│              └─────────────────────┘                           │
│                         │                                       │
│                         ▼                                       │
│              ┌─────────────────────┐                           │
│              │  External Systems   │                           │
│              │  (LMS, SIS, Email)  │                           │
│              └─────────────────────┘                           │
└─────────────────────────────────────────────────────────────────┘
```

### Level 2: Container Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         CampusIQ                                 │
│                                                                  │
│  ┌──────────────┐         ┌─────────────────────────────┐      │
│  │   Browser    │────────▶│   Next.js Frontend          │      │
│  │   (User)     │         │   (React, TypeScript)        │      │
│  └──────────────┘         └─────────────────────────────┘      │
│                                     │                          │
│                                     │ HTTPS/JSON               │
│                                     ▼                          │
│                           ┌─────────────────────┐              │
│                           │   FastAPI Backend   │              │
│                           │   (Python, Async)   │              │
│                           └─────────────────────┘              │
│                                     │                          │
│                   ┌─────────────────┼─────────────────┐        │
│                   ▼                 ▼                 ▼        │
│           ┌──────────┐      ┌──────────┐      ┌──────────┐    │
│           │PostgreSQL│      │  Redis   │      │  Ollama  │    │
│           │+pgvector │      │ (Cache)  │      │  (LLM)   │    │
│           └──────────┘      └──────────┘      └──────────┘    │
│                                                                  │
│  Supporting Services:                                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                      │
│  │ Airflow  │  │  MLflow  │  │  Grafana │                      │
│  │  (ETL)   │  │(Tracking)│  │(Monitor) │                      │
│  └──────────┘  └──────────┘  └──────────┘                      │
└─────────────────────────────────────────────────────────────────┘
```

### Level 3: Component Diagram (Backend)

```
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                               │
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │   Router    │  │   Auth      │  │    Rate Limiter         │ │
│  │             │  │  Middleware │  │    (Redis)              │ │
│  └──────┬──────┘  └─────────────┘  └─────────────────────────┘ │
│         │                                                        │
│    ┌────┴────┬────────────┬────────────┐                       │
│    ▼         ▼            ▼            ▼                       │
│ ┌──────┐ ┌──────┐  ┌──────────┐  ┌──────────┐                │
│ │Auth  │ │Student│  │Prediction│  │   RAG    │                │
│ │API   │ │ API   │  │   API    │  │   API    │                │
│ └──┬───┘ └──┬───┘  └────┬─────┘  └────┬─────┘                │
│    │        │           │             │                        │
│    ▼        ▼           ▼             ▼                        │
│ ┌─────────────────────────────────────────────┐               │
│ │           Service Layer                      │               │
│ │  ┌────────────┐  ┌────────────┐             │               │
│ │  │ Prediction │  │    RAG     │  ┌────────┐ │               │
│ │  │  Service   │  │  Service   │  │  JWT   │ │               │
│ │  │(XGBoost)   │  │(LangChain) │  │Service │ │               │
│ │  └────────────┘  └────────────┘  └────────┘ │               │
│ └─────────────────────────────────────────────┘               │
│                              │                                  │
│                              ▼                                  │
│                    ┌─────────────────┐                         │
│                    │   Data Access   │                         │
│                    │  (SQLAlchemy)   │                         │
│                    └─────────────────┘                         │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Prediction Request Flow
```
1. Faculty clicks "Analyze" on student profile
2. Frontend POST /api/v1/predictions/predict/{student_id}
3. Auth middleware validates JWT
4. PredictionService.extract_features(student) → numpy array
5. Model.predict_proba(features) → risk_score
6. Risk categorization + factor analysis
7. Save to PostgreSQL predictions table
8. Return risk_score, category, top_factors to frontend
```

### RAG Chat Flow
```
1. Student types question in chat UI
2. Frontend POST /api/v1/chat/message
3. Auth middleware validates JWT
4. RAGService.embed_query(question) → 384-dim vector
5. pgvector cosine similarity search → top-5 documents
6. Build prompt with context + question
7. Ollama.generate(prompt) → streaming response
8. Save to chat_history table
9. Return response + sources to frontend
```

## Infrastructure Diagram (AWS)

```
┌─────────────────────────────────────────────────────────────────┐
│                         AWS Cloud                                │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                      VPC (10.0.0.0/16)                   │   │
│  │                                                         │   │
│  │  ┌─────────────┐              ┌─────────────────────┐   │   │
│  │  │  Public     │              │      Private        │   │   │
│  │  │  Subnets    │              │      Subnets        │   │   │
│  │  │             │              │                     │   │   │
│  │  │ ┌─────────┐ │              │ ┌─────────────────┐ │   │   │
│  │  │ │   ALB   │ │              │ │   ECS Fargate   │ │   │   │
│  │  │ │(HTTPS)  │ │──────────────│ │   (Backend)     │ │   │   │
│  │  │ └─────────┘ │              │ └─────────────────┘ │   │   │
│  │  │      │      │              │ ┌─────────────────┐ │   │   │
│  │  │ ┌────┴────┐ │              │ │   ECS Fargate   │ │   │   │
│  │  │ │   WAF   │ │              │ │   (Frontend)    │ │   │   │
│  │  │ └─────────┘ │              │ └─────────────────┘ │   │   │
│  │  └─────────────┘              │ ┌─────────────────┐ │   │   │
│  │                               │ │   RDS Postgres  │ │   │   │
│  │                               │ │   + pgvector    │ │   │   │
│  │                               │ └─────────────────┘ │   │   │
│  │                               └─────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐                      │
│  │   ECR Repos     │  │    S3 Buckets   │                      │
│  │ (Docker Images) │  │ (Artifacts/Logs)│                      │
│  └─────────────────┘  └─────────────────┘                      │
└─────────────────────────────────────────────────────────────────┘
```

## Technology Stack Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        TECHNOLOGY STACK                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  PRESENTATION LAYER                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │  Next.js 14  │  │  Tailwind CSS│  │     Recharts         │  │
│  │  TypeScript  │  │  Lucide Icons│  │     (Viz)            │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│                                                                 │
│  APPLICATION LAYER                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │   FastAPI    │  │   Pydantic   │  │   SQLAlchemy         │  │
│  │   Python 3.11│  │   (Validation)│  │   (ORM)             │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│                                                                 │
│  AI/ML LAYER                                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │   XGBoost    │  │  LangChain   │  │  sentence-transformers│  │
│  │  (Predict)   │  │    (RAG)     │  │   (Embeddings)       │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│                                                                 │
│  DATA LAYER                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │  PostgreSQL  │  │   pgvector   │  │      Redis           │  │
│  │   (RDS)      │  │ (Embeddings) │  │    (ElastiCache)     │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│                                                                 │
│  DEVOPS LAYER                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │    Docker    │  │   Terraform  │  │   GitHub Actions     │  │
│  │  (Container) │  │    (IaC)     │  │     (CI/CD)          │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```
