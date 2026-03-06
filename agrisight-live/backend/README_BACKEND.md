# AgriSight Live Backend

FastAPI application for orchestrating Gemini Live sessions.

## Setup
1. `pip install -r requirements.txt` (or use poetry)
2. `uvicorn app.main:app --reload`

## Environment Variables
- `MOCK_GEMINI`: Set to `true` to bypass actual Gemini API calls.
- `GEMINI_API_KEY`: Required if `MOCK_GEMINI` is false.
