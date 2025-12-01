# Python Project

A Python application with CLI and RESTful API interfaces, managed with UV.

## Project Structure

```
.
├── src/
│   └── app/
│       ├── api/          # REST API endpoints
│       ├── cli/          # CLI commands
│       ├── core/         # Core business logic
│       ├── models/       # Data models
│       ├── services/     # Service layer
│       └── utils/        # Utility functions
├── tests/
│   ├── unit/            # Unit tests
│   └── integration/     # Integration tests
├── docs/                # Documentation
├── pyproject.toml       # Project configuration
└── README.md           # This file
```

## Setup

1. Install UV (if not already installed):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Install dependencies:
```bash
uv sync
```

3. Install development dependencies:
```bash
uv sync --dev
```

## Usage

### CLI

```bash
uv run app-cli --help
```

### REST API

Start the development server:
```bash
uv run uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000
```

Or start the production server:
```bash
uv run uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

Access the API:
- API Documentation: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health
- API Endpoints: http://localhost:8000/api/v1/

## Development

### Run tests
```bash
uv run pytest
```

### Run linter
```bash
uv run ruff check .
```

### Type checking
```bash
uv run mypy src/
```
