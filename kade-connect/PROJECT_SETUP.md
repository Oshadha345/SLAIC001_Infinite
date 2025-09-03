# Kade Connect - Complete Development Setup Guide

## 🎯 Project Overview
AI-powered grocery shopping platform connecting Sri Lankan consumers with supermarkets and local 'kade' shops using 5 specialized AI agents.

## 📁 Project Structure
```
kade-connect/
├── backend/                 # Python FastAPI microservices
│   ├── agents/             # 5 AI Agents
│   ├── services/           # Core microservices
│   ├── shared/             # Common utilities
│   └── docker/             # Container configurations
├── frontend/               # React Native mobile app
│   ├── mobile/             # React Native app
│   └── web/                # Optional web dashboard
├── infrastructure/         # Docker, K8s, CI/CD
├── scripts/               # Setup and deployment scripts
├── docs/                  # Documentation
└── tests/                 # Test suites

```

## 🛠️ Technology Stack

### Backend
- **Language**: Python 3.11+
- **Framework**: FastAPI
- **AI/ML**: LangChain, LangGraph, Pydantic AI
- **Database**: PostgreSQL with pgvector
- **Cache**: Redis
- **Message Queue**: RabbitMQ
- **Authentication**: Supabase Auth
- **File Storage**: AWS S3 / Supabase Storage

### Frontend
- **Framework**: React Native (Expo)
- **State Management**: Redux Toolkit
- **UI Library**: NativeBase with custom Serendib theme
- **Maps**: Google Maps API
- **Voice**: React Native Voice

### Infrastructure
- **Containerization**: Docker
- **Orchestration**: Docker Compose (dev), Kubernetes (prod)
- **CI/CD**: GitHub Actions
- **Cloud**: AWS / Supabase
- **Monitoring**: Sentry

## 🔧 Development Environment Setup

### Prerequisites Installation (Windows)
Run the following commands in PowerShell (as Administrator):

```powershell
# Install Chocolatey
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install development tools
choco install -y git python311 nodejs docker-desktop vscode postgresql redis
choco install -y microsoft-windows-terminal
```

### Project Dependencies
See individual setup scripts in `/scripts/` folder for detailed installation.

## 🔑 Required API Keys & Configuration

Before starting development, you'll need to obtain the following API keys:

1. **OpenAI API Key** - For AI agents
2. **Google Cloud Vision API** - For OCR processing
3. **Google Maps API** - For location services
4. **Supabase Project** - For auth and database
5. **Stripe API Keys** - For payment processing
6. **AWS Account** - For S3 storage (optional, can use Supabase)

## 🚀 Quick Start

1. Clone and setup:
```bash
cd s:\Projects\SLAIC001_Infinite\kade-connect
.\scripts\setup-development.ps1
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. Start development environment:
```bash
docker-compose up -d
```

4. Run the application:
```bash
# Backend
cd backend && uvicorn main:app --reload

# Frontend
cd frontend/mobile && expo start
```

## 📋 Development Checklist

- [ ] Environment setup complete
- [ ] API keys configured
- [ ] Database migrations run
- [ ] All services running
- [ ] Mobile app builds successfully
- [ ] Tests passing

## 🏗️ Development Phases

### Phase 1: Core Infrastructure (Week 1-2)
- [ ] Project structure and dependencies
- [ ] Database schema and migrations
- [ ] Authentication system
- [ ] Basic API endpoints
- [ ] Docker containerization

### Phase 2: AI Agents Development (Week 3-4)
- [ ] Data Acquisition Agent
- [ ] Budget Optimization Agent
- [ ] Personalization Agent
- [ ] Logistics Agent
- [ ] Execution Agent

### Phase 3: Frontend Development (Week 5-6)
- [ ] React Native app structure
- [ ] Serendib UI theme
- [ ] Consumer mode features
- [ ] Partner mode features
- [ ] Voice interface

### Phase 4: Integration & Testing (Week 7-8)
- [ ] End-to-end testing
- [ ] Performance optimization
- [ ] Security auditing
- [ ] Deployment preparation

## 📞 Support & Documentation

- **Technical Issues**: Check `/docs/troubleshooting.md`
- **API Documentation**: Auto-generated at `/docs` endpoint
- **Architecture**: See `/docs/architecture.md`
- **Contributing**: See `CONTRIBUTING.md`
