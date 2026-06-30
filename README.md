# ArmorIQ Backend

FastAPI backend for ArmorIQ with PydanticAI agent integration.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
# Copy .env template and fill in your API keys
cp .env.example .env
```

4. Run the server:
```bash
python app.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

- `GET /` - Welcome message
- `GET /health` - Health check
- `POST /chat` - Chat with the AI agent

## Project Structure

- `app.py` - FastAPI application entry point
- `agent.py` - PydanticAI agent configuration
- `config.py` - Configuration and environment variables
- `requirements.txt` - Python dependencies
- `.env` - Environment variables (not committed to git)

## Environment Variables

- `OPENAI_API_KEY` - Your OpenAI API key
- `DATABASE_URL` - Database connection URL
- `DEBUG` - Debug mode (True/False)
