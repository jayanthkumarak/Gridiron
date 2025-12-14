# Gridiron

NFL Analytics powered by natural language. Ask questions, get insights.

## Quick Start

### Prerequisites

- Docker Desktop
- OpenRouter API key

### Setup

1. **Configure environment**
   ```bash
   cp api/.env.example api/.env
   # Edit api/.env with your OPENROUTER_API_KEY
   ```

2. **Start services**
   ```bash
   docker-compose up
   ```

3. **Open app**
   - Frontend: http://localhost:5173
   - API: http://localhost:8000
   - R Service: http://localhost:8787

## Development

### Frontend (SvelteKit)
```bash
cd app
npm install
npm run dev
```

### Backend (FastAPI)
```bash
cd api
pip install -r requirements.txt
uvicorn main:app --reload
```

### R Service
```bash
cd r-service
docker build -t gridiron-r .
docker run -p 8787:8787 gridiron-r
```

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  SvelteKit  │────▶│   FastAPI   │────▶│  R Service  │
│   :5173     │     │   :8000     │     │   :8787     │
└─────────────┘     └──────┬──────┘     └─────────────┘
                          │
                          ▼
                   ┌─────────────┐
                   │  OpenRouter │
                   │  (Claude)   │
                   └─────────────┘
```

## Tech Stack

- **Frontend**: SvelteKit, TypeScript, Apache ECharts
- **Backend**: FastAPI, Python
- **Analytics**: R, nflfastR, Plumber
- **LLM**: OpenRouter (Claude 3.5 Sonnet)

## License

MIT
