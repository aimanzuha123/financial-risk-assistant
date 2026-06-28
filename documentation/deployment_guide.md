# Production Deployment Guide

This guide outlines production deployment steps for the **AI Financial Risk & Collections Assistant**.

## 1. Cloud Architecture

```
Internet -> Load Balancer (HTTPS) -> Nginx (Frontend Service)
                                      |
                                      +--> FastAPI (Backend API Service)
                                            |
                                            +--> SQLite / PostgreSQL
```

## 2. Docker Orchestration

The application contains Dockerfiles for both services.

### Build and Run locally
```bash
docker-compose up -d --build
```

### Environment Variables
Configure these variables in production:
- `SECRET_KEY`: High entropy string to secure cookies and sessions.
- `OPENAI_API_KEY`: API token for GPT-4 assistant features.
- `PORT`: Listen port for FastAPI server.

## 3. Database Migration
In a enterprise setting, migrate SQLite to PostgreSQL:
Update `DATABASE_URL` in config settings to:
`postgresql://user:password@host:port/dbname`
FastAPI's SQLAlchemy setup will auto-generate table structures on startup.
