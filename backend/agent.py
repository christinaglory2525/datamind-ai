import os
import json
import re
from functools import lru_cache

from dotenv import load_dotenv
from google import genai

from backend.tools import (
    get_schema,
    execute_query,
    generate_chart,
    generate_flowchart,
)

# Load .env
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY is missing. Check your .env file.")

# Gemini client
client = genai.Client(api_key=API_KEY)


# ---------------------------------------------------------
# DATABASE SCHEMA
# ---------------------------------------------------------

@lru_cache(maxsize=1)
def cached_schema():
    return get_schema()


# ---------------------------------------------------------
# GEMINI SQL GENERATION
# ---------------------------------------------------------

def generate_sql(question: str, schema: dict) -> str:
    """Convert a natural-language question into SQL."""

    schema_text = json.dumps(schema, indent=2)

    prompt = f"""
You are an expert SQLite SQL analyst.

DATABASE SCHEMA:
{schema_text}

USER QUESTION:
{question}

Write ONE SQLite SELECT query that answers the question.

Rules:
1. Only SELECT or WITH queries.
2. Never INSERT, UPDATE, DELETE, DROP, ALTER, or CREATE.
3. Use only tables and columns that exist in the schema.
4. For product revenue, use products.price * order_items.quantity.
5. Return ONLY SQL.
6. Do not use markdown.

Important schema:
products:
product_id, name, category, price

order_items:
order_item_id, order_id, product_id, quantity

Example:
SELECT p.name,
       SUM(p.price * oi.quantity) AS revenue
FROM products p
JOIN order_items oi
ON p.product_id = oi.product_id
GROUP BY p.product_id, p.name
ORDER BY revenue DESC
LIMIT 5;
"""

    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt,
    )

    sql = response.text.strip()

    sql = re.sub(r"```sql", "", sql, flags=re.IGNORECASE)
    sql = re.sub(r"```", "", sql)

    return sql.strip()


# ---------------------------------------------------------
# FAST SQL FOR COMMON HACKATHON QUESTIONS
# ---------------------------------------------------------

def fast_query(question: str):
    q = question.lower().strip()

    # TOP 5 PRODUCTS BY REVENUE
    if "top 5 products by revenue" in q:
        return """
        SELECT
            p.name,
            SUM(p.price * oi.quantity) AS revenue
        FROM products p
        JOIN order_items oi
            ON p.product_id = oi.product_id
        GROUP BY p.product_id, p.name
        ORDER BY revenue DESC
        LIMIT 5
        """.strip()

    # HIGHEST PRICED PRODUCTS
    if "highest priced products" in q:
        return """
        SELECT name, price
        FROM products
        ORDER BY price DESC
        LIMIT 5
        """.strip()

    # PRODUCTS BY CATEGORY
    if "products by category" in q:
        return """
        SELECT category, COUNT(*) AS product_count
        FROM products
        GROUP BY category
        ORDER BY product_count DESC
        """.strip()

    # SHOW ALL CUSTOMERS
    if "show all customers" in q:
        return """
        SELECT *
        FROM customers
        """.strip()

    return None


# ---------------------------------------------------------
# MAIN AI WORKFLOW
# ---------------------------------------------------------

def process_question(question: str) -> dict:
    """Run the complete AI database workflow."""

    # -----------------------------------------------------
    # ER DIAGRAM
    # -----------------------------------------------------

    diagram_keywords = [
        "er diagram",
        "erd",
        "entity relationship",
        "database diagram",
        "schema diagram",
        "relationship diagram",
    ]

    if any(keyword in question.lower() for keyword in diagram_keywords):

        schema = cached_schema()

        diagram = generate_flowchart(schema)

        return {
            "success": diagram["success"],
            "question": question,
            "diagram": diagram,
        }

    try:

        # -------------------------------------------------
        # STEP 1: GET SCHEMA
        # -------------------------------------------------

        schema = cached_schema()

        # -------------------------------------------------
        # STEP 2: FAST PATH
        # -------------------------------------------------

        sql = fast_query(question)

        # -------------------------------------------------
        # STEP 3: GEMINI ONLY IF NEEDED
        # -------------------------------------------------

        if sql is None:
            sql = generate_sql(question, schema)

        # -------------------------------------------------
        # STEP 4: EXECUTE SQL
        # -------------------------------------------------

        result = execute_query(sql)

        if not result["success"]:
            return {
                "success": False,
                "question": question,
                "sql": sql,
                "error": result["error"],
            }

        # -------------------------------------------------
        # STEP 5: LOCAL EXPLANATION
        # NO SECOND AI CALL
        # -------------------------------------------------

        rows = result.get("rows", [])

        if rows:

            columns = ", ".join(rows[0].keys())

            explanation = (
                f"The query returned {len(rows)} results. "
                f"The result contains the columns: {columns}."
            )

            # Special explanation for revenue
            if "revenue" in rows[0]:

                highest = rows[0]

                if "name" in highest:
                    explanation = (
                        f"The query returned {len(rows)} results. "
                        f"The highest revenue product is "
                        f"{highest['name']} with revenue of "
                        f"{highest['revenue']}."
                    )

        else:
            explanation = "The query returned no results."

        # -------------------------------------------------
        # STEP 6: GENERATE CHART
        # -------------------------------------------------

        chart = generate_chart(
            result,
            chart_type="bar",
            title=question,
        )

        # -------------------------------------------------
        # FINAL RESPONSE
        # -------------------------------------------------

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


# ---------------------------------------------------------
# TEST
# ---------------------------------------------------------

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