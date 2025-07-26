# Natural Language to SQL API

A minimal Python backend that converts natural language queries to SQL, executes them on a database, and returns both tabular data and Plotly charts.

## Features

- FastAPI HTTP API
- SQLAlchemy with SQLite (instant setup)
- OpenAI-compatible client (works with OpenAI, Claude proxies, vLLM, etc.)
- Automatic Plotly chart generation
- Sample sales data included

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set your API key:
```bash
export OPENAI_API_KEY="your-api-key-here"
# Optional: Set custom base URL for other providers
export OPENAI_BASE_URL="https://api.openai.com/v1"
```

3. Initialize sample data:
```bash
python database.py
```

4. Run the server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## Usage

### Query Endpoint
POST `/query`
```json
{
  "query": "Show me total sales by category",
  "model": "gpt-3.5-turbo"
}
```

Response includes:
- Generated SQL query
- Query results as JSON
- Interactive Plotly chart as HTML

### Other Endpoints
- GET `/` - API info
- GET `/tables` - Database schema
- GET `/docs` - Interactive API documentation

## Example Queries

- "Show me total sales by region"
- "What are the top 5 products by quantity sold?"
- "Compare sales amounts between Electronics and Furniture categories"
- "Show monthly sales trends"

## Database Schema

The sample database includes a `sales` table with:
- product, category, region (strings)
- sales_amount (float), quantity (integer)
- date (datetime)

## Configuration

- Database: Modify `DATABASE_URL` in `main.py`
- Model: Change default model in the request
- Base URL: Set `OPENAI_BASE_URL` environment variable