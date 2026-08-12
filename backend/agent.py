import os
import json
import re

from dotenv import load_dotenv
from google import genai

from backend.tools import (
    get_schema,
    execute_query,
    generate_chart,
    generate_flowchart,
    explain_data,
)

# Load .env
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is missing. Check your .env file."
    )

# Create Gemini client
client = genai.Client(api_key=API_KEY)


def generate_sql(question: str, schema: dict) -> str:
    """Convert a natural-language question into SQL."""

    schema_text = json.dumps(schema, indent=2)

    prompt = f"""
You are an expert SQL analyst.

You are working with a SQLite e-commerce database.

DATABASE SCHEMA:
{schema_text}

USER QUESTION:
{question}

Your task:
Write ONE SQLite SQL query that answers the user's question.

Rules:
1. Only use SELECT or WITH queries.
2. Never INSERT, UPDATE, DELETE, DROP, ALTER, or CREATE.
3. Use only tables and columns that exist in the schema.
4. Return ONLY the SQL query.
5. Do not use markdown code blocks.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    sql = response.text.strip()

    # Remove markdown fences if Gemini adds them
    sql = re.sub(r"```sql", "", sql, flags=re.IGNORECASE)
    sql = re.sub(r"```", "", sql)

    return sql.strip()


def process_question(question: str) -> dict:
    """Run the complete AI database workflow."""

    # Handle ER diagram requests
    diagram_keywords = [
        "er diagram",
        "erd",
        "entity relationship",
        "database diagram",
        "schema diagram",
        "relationship diagram"
    ]

    if any(keyword in question.lower() for keyword in diagram_keywords):

        schema = get_schema()

        diagram = generate_flowchart(schema)

        return {
            "success": diagram["success"],
            "question": question,
            "diagram": diagram
        }

    try:

        # Step 1: Get database schema
        schema = get_schema()

        # Step 2: Convert question → SQL
        sql = generate_sql(question, schema)

        # Step 3: Execute SQL
        result = execute_query(sql)

        if not result["success"]:
            return {
                "success": False,
                "question": question,
                "sql": sql,
                "error": result["error"],
            }

        # Step 4: Explain result
        explanation = explain_data(result)

        # Step 5: Generate chart
        chart = generate_chart(
            result,
            chart_type="bar",
            title=question,
        )

        return {
            "success": True,
            "question": question,
            "sql": sql,
            "data": result,
            "explanation": explanation,
            "chart": chart,
        }

    except Exception as error:

        return {
            "success": False,
            "question": question,
            "error": str(error),
        }
if __name__ == "__main__":

    question = "What are the top 5 products by revenue?"

    print("\n========================================")
    print("🤖 DATA INTELLIGENCE AGENT")
    print("========================================")

    print("\n👤 QUESTION:")
    print(question)

    result = process_question(question)

    print("\n🧠 AGENT RESULT:")
    print(json.dumps(result, indent=2))

    print("\n========================================")