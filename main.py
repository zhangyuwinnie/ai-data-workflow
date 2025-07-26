from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, text, MetaData
from sqlalchemy.orm import sessionmaker
import openai
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json
import os
import datetime
from typing import Dict, Any, List

app = FastAPI(title="Natural Language to SQL API")

DATABASE_URL = "sqlite:///./data.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

openai_client = openai.OpenAI(
    api_key=os.getenv("OPENAI_API_KEY", "your-api-key-here"),
    base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
)

class QueryRequest(BaseModel):
    query: str
    model: str = "gpt-3.5-turbo"

class QueryResponse(BaseModel):
    sql: str
    data: List[Dict[str, Any]]
    chart_html: str

@app.get("/")
async def root():
    return {"message": "Natural Language to SQL API"}

@app.get("/tables")
async def get_tables():
    with engine.connect() as conn:
        metadata = MetaData()
        metadata.reflect(bind=engine)
        tables = {}
        for table_name in metadata.tables:
            table = metadata.tables[table_name]
            columns = [{"name": col.name, "type": str(col.type)} for col in table.columns]
            tables[table_name] = {"columns": columns}
    return tables

def get_schema_info():
    with engine.connect() as conn:
        metadata = MetaData()
        metadata.reflect(bind=engine)
        schema_info = []
        for table_name in metadata.tables:
            table = metadata.tables[table_name]
            columns = [f"{col.name} ({col.type})" for col in table.columns]
            schema_info.append(f"Table: {table_name}\nColumns: {', '.join(columns)}")
    return "\n\n".join(schema_info)

def natural_language_to_sql(query: str, model: str) -> str:
    schema = get_schema_info()
    
    prompt = f"""You are a SQL expert. Convert the following natural language query to SQL.

Database Schema:
{schema}

Natural Language Query: {query}

Rules:
1. Return ONLY the SQL query, no explanations
2. Use SQLite syntax
3. Be precise with table and column names
4. Use appropriate WHERE clauses, JOINs, and aggregations as needed

SQL Query:"""

    response = openai_client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    
    return response.choices[0].message.content.strip()

def execute_sql(sql: str) -> List[Dict[str, Any]]:
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        columns = result.keys()
        rows = result.fetchall()
        return [dict(zip(columns, row)) for row in rows]

def generate_chart(data: List[Dict[str, Any]], original_query: str) -> str:
    if not data:
        return "<p>No data to display</p>"
    
    df = pd.DataFrame(data)
    
    if len(df.columns) == 1:
        fig = go.Figure(data=[go.Bar(x=df.index, y=df.iloc[:, 0])])
        fig.update_layout(title=f"Results for: {original_query}")
    elif len(df.columns) == 2:
        col1, col2 = df.columns[0], df.columns[1]
        if df[col2].dtype in ['int64', 'float64']:
            fig = go.Figure(data=[go.Bar(x=df[col1], y=df[col2])])
        else:
            fig = go.Figure(data=[go.Bar(x=df[col1], y=df.index)])
        fig.update_layout(title=f"Results for: {original_query}", xaxis_title=col1, yaxis_title=col2)
    else:
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) >= 2:
            fig = px.scatter(df, x=numeric_cols[0], y=numeric_cols[1], title=f"Results for: {original_query}")
        else:
            fig = go.Figure(data=[go.Table(
                header=dict(values=list(df.columns)),
                cells=dict(values=[df[col].tolist() for col in df.columns])
            )])
    
    chart_html = fig.to_html(include_plotlyjs='cdn')
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_query = "".join(c if c.isalnum() or c in (' ', '-', '_') else '' for c in original_query)
    safe_query = safe_query.replace(' ', '_')[:50]
    filename = f"chart_{safe_query}_{timestamp}.html"
    
    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Query Results: {original_query}</title>
</head>
<body>
    <h1>Query Results</h1>
    <p><strong>Query:</strong> {original_query}</p>
    <div>
        {chart_html}
    </div>
</body>
</html>"""
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(full_html)
    
    print(f"Chart saved as: {filename}")
    return chart_html

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    try:
        sql = natural_language_to_sql(request.query, request.model)
        data = execute_sql(sql)
        chart_html = generate_chart(data, request.query)
        
        return QueryResponse(
            sql=sql,
            data=data,
            chart_html=chart_html
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)