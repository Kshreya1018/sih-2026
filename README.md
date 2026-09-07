# medi-locator-api

Emergency medical triage and nearby medical facility locator API built with FastAPI, Groq LLM (llama-3.3-70b-versatile), and OpenStreetMap (Overpass API).

---

## Running Locally (No Docker)

Follow these steps to set up and run the service directly on your host machine without Docker:

### 1. Create a virtual environment
```bash
python -m venv venv
```

### 2. Activate the virtual environment
- **macOS / Linux:**
  ```bash
  source venv/bin/activate
  ```
- **Windows (PowerShell):**
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
- **Windows (Command Prompt):**
  ```cmd
  .\venv\Scripts\activate.bat
  ```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Create `.env` configuration
Copy the sample environment file to `.env`:
- **macOS / Linux:**
  ```bash
  cp .env.example .env
  ```
- **Windows:**
  ```powershell
  copy .env.example .env
  ```

Open `.env` and configure your `GROQ_API_KEY`:
```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
OVERPASS_API_URL=https://overpass-api.de/api/interpreter
DEFAULT_SEARCH_RADIUS=5000
```
> **Note:** The `GROQ_API_KEY` is required for live LLM triage classification with Groq. If not set, the API operates safely with built-in emergency fallback heuristics.

### 5. Run the server
```bash
uvicorn app.main:app --reload
```

### 6. Confirm it's running
Open your browser or run curl to test:
- **Health check:** [http://localhost:8000/health](http://localhost:8000/health)
- **Interactive Swagger Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Alternative ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## API Endpoints

### `GET /health`
Returns service health status:
```json
{
  "status": "healthy",
  "service": "medi-locator-api",
  "version": "1.0.0"
}
```

### `POST /find-help`
Accepts user symptom text and geographic coordinates, classifies medical urgency and category, and queries nearby facilities within radius:

**Request:**
```json
{
  "text": "I have severe chest pain and can't breathe",
  "lat": 28.6139,
  "lng": 77.2090
}
```

**Response:**
```json
{
  "needs": "hospital",
  "specialty": "General Medicine",
  "urgency": "high",
  "results": [
    {
      "name": "Dr. Ram Manohar Lohia Hospital",
      "type": "hospital",
      "distance_km": 1.57,
      "lat": 28.6260617,
      "lng": 77.2007463,
      "address": "Baba Kharak Singh Marg, Near Bangla Sahib Gurudwara",
      "phone": "011-22344470"
    }
  ]
}
```
