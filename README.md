# Waybill Shipping Assistant API

A FastAPI-based intelligent shipping assistant that provides shipment tracking, rate quotes, and pickup location information through a natural language chat interface.

## Features

- **Shipment Tracking**: Track packages using tracking IDs with real-time status updates
- **Rate Quotes**: Get shipping rates between different cities with weight-based pricing
- **Pickup Locations**: Find nearby pickup points in various cities
- **Natural Language Processing**: Intent classification and parameter extraction from user messages
- **Document Retrieval**: RAG-based system with shipping policies, terms, and zone information
- **PII Guardrails**: Built-in protection for sensitive information

## Tech Stack

- **Framework**: FastAPI
- **Vector Store**: ChromaDB for document retrieval
- **NLP**: Spacy for text processing
- **LLM Integration**: OpenAI API
- **Testing**: Pytest with async support
- **Deployment**: Uvicorn ASGI server, Docker support

## Prerequisites

- Python 3.9+
- pip or uv for package management

## Setup Instructions

### 1. Create Virtual Environment

```bash
python -m venv venv
```

### 2. Activate Virtual Environment

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
.\venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## Running the Server

Start the FastAPI server with Uvicorn:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output:**
```
INFO:     Will watch for changes in these directories: ['C:\\Users\\UserPc\\Desktop\\workspace\\waybill']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using WatchFiles
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

The API will be available at `http://localhost:8000`

## API Endpoints & Demo Examples

### Health Check

Verify the server is running:

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "ok": true
}
```

---

### Chat Endpoint - Track Shipment

Track a package using its tracking ID:

```bash
curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d "{\"message\": \"track 1Z12345\"}"
```

**Response:**
```json
{
  "intent": "track",
  "tool": "track_shipment",
  "*args": {
    "tracking_id": "1Z12345"
  },
  "result": {
    "tracking_id": "1Z12345",
    "status": "In Transit",
    "last_scan": "2025-10-18T15:42:00Z",
    "origin": "Seoul",
    "destination": "Prague",
    "eta_days": 4
  },
  "answer": "Status: In Transit. Last scan: 2025-10-18T15:42:00Z. Estimated arrival: 4 days.",
  "ok": true
}
```

**Alternative tracking ID:**
```bash
curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d "{\"message\": \"track ABC999\"}"
```

---

### Chat Endpoint - Get Shipping Rates

Get rate quotes between cities:

```bash
curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d "{\"message\": \"rates from Seoul to Prague 2kg\"}"
```

**Response:**
```json
{
  "intent": "rates",
  "tool": "get_rates",
  "args": {
    "origin": "Seoul",
    "dest": "Prague",
    "weight_kg": 2.0
  },
  "result": [
    {
      "service": "Express",
      "origin": "Seoul",
      "destination": "Prague",
      "price_usd": 52.0,
      "transit_days": 3,
      "quote_usd": 59.8,
      "weight_kg": 2.0
    },
    {
      "service": "Economy",
      "origin": "Seoul",
      "destination": "Prague",
      "price_usd": 34.5,
      "transit_days": 6,
      "quote_usd": 39.68,
      "weight_kg": 2.0
    }
  ],
  "answer": "Best rate Economy: $39.68 for 2.0kg, ~6 day(s).",
  "ok": true
}
```

**Different route:**
```bash
curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d "{\"message\": \"rates from Cyberjaya to Seoul 1kg\"}"
```

---

### Chat Endpoint - Find Pickup Locations

Find pickup points in a specific city:

```bash
curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d "{\"message\": \"nearest pickup location in Seoul\"}"
```

**Response:**
```json
{
  "intent": "locations",
  "tool": "find_locations",
  "args": {
    "city": "Seoul"
  },
  "result": [
    {
      "city": "Seoul",
      "name": "Dongdaemun ServicePoint",
      "address": "123 Market St"
    }
  ],
  "answer": "Pickup points in Seoul: Dongdaemun ServicePoint.",
  "ok": true
}
```

**Other cities:**
```bash
curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d "{\"message\": \"pickup locations in Prague\"}"
```

---

### Natural Language Variations

The agent understands various ways of asking:

**Tracking:**
- "track 1Z12345"
- "where is my package 1Z12345"
- "status of ABC999"

**Rates:**
- "rates from Seoul to Prague 2kg"
- "how much to ship from Seoul to Prague 2kg"
- "price from Cyberjaya to Seoul"

**Locations:**
- "nearest pickup location in Seoul"
- "pickup points in Prague"
- "where can I drop off in Cyberjaya"

## Project Architecture

```
app/
├── main.py                 # FastAPI application entry point
├── config.py              # Configuration and paths
├── router_chat.py         # Chat router (deprecated, see routers/)
├── data/
│   └── seed.json          # Sample shipment, rate, and location data
├── guardrails/
│   └── pii.py            # PII detection and protection
├── llm/
│   ├── client.py         # OpenAI client wrapper
│   └── chain.py          # LLM chain orchestration
├── retrieval/
│   ├── docs/             # Policy documents (policies.md, terms.md, zones.md)
│   ├── ingest.py         # Document ingestion to vector store
│   └── store.py          # ChromaDB vector store management
├── routers/
│   ├── chat.py           # Chat API endpoints
│   └── health.py         # Health check endpoints
├── services/
│   ├── agent.py          # Intent classification and agent logic
│   └── tools.py          # Core tools (track, rates, locations)
├── mock/
│   ├── mock_shipments.json   # Additional mock data
│   └── router_mock.py        # Mock endpoints for testing
└── tests/
    ├── test_chat.py
    ├── test_guardrails.py
    └── test_llm_call.py
```

### Key Components

**Agent (`services/agent.py`)**
- Intent classification using regex patterns
- Parameter extraction from natural language
- Tool orchestration and response formatting

**Tools (`services/tools.py`)**
- `track_shipment()`: Query shipment status by tracking ID
- `get_rates()`: Calculate shipping rates with weight-based pricing
- `find_locations()`: Search pickup locations by city

**Retrieval (`retrieval/`)**
- Document ingestion on startup
- ChromaDB vector store for semantic search
- Policy, terms, and zone documentation

**Guardrails (`guardrails/pii.py`)**
- PII detection using Spacy NER
- Redaction of sensitive information

## Running Tests

```bash
pytest app/tests/ -v
```

## Docker Deployment

Build and run with Docker:

```bash
docker build -t waybill-api .
docker run -p 8000:8000 waybill-api
```

## API Documentation

Once the server is running, access interactive API docs:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Sample Data

The application includes sample data for demonstration:

- **2 Shipments**: Active tracking IDs (1Z12345, ABC999)
- **3 Rate Routes**: Seoul↔Prague, Cyberjaya→Seoul
- **3 Pickup Locations**: Seoul, Cyberjaya, Prague

## Environment Variables

Create a `.env` file for configuration (optional):

```env
OPENAI_API_KEY=your_key_here
LOG_LEVEL=INFO
```