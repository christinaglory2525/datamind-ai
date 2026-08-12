import sqlite3
from pathlib import Path
from typing import Any

import plotly.express as px


# ============================================================
# PATHS
# ============================================================

DB_PATH = Path(__file__).parent / "data" / "company.db"
CHART_DIR = Path(__file__).parent.parent / "frontend" / "charts"


# ============================================================
# DATABASE SCHEMA
# ============================================================

def get_schema() -> dict[str, Any]:
    """Return database tables, columns, and relationships."""

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    tables = {}

    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """)

    table_names = [row[0] for row in cursor.fetchall()]

    for table in table_names:

        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()

        tables[table] = {
            "columns": [
                {
                    "name": column[1],
                    "type": column[2],
                    "primary_key": bool(column[5])
                }
                for column in columns
            ]
        }

    relationships = []

    for table in table_names:

        cursor.execute(f"PRAGMA foreign_key_list({table})")

        for row in cursor.fetchall():

            relationships.append({
                "from_table": table,
                "from_column": row[3],
                "to_table": row[2],
                "to_column": row[4]
            })

    connection.close()

    return {
        "tables": tables,
        "relationships": relationships
    }


# ============================================================
# SQL QUERY EXECUTION
# ============================================================

def execute_query(sql: str) -> dict[str, Any]:
    """Execute a read-only SQL query."""

    sql_clean = sql.strip().lower()

    if not sql_clean.startswith(("select", "with", "pragma")):
        return {
            "success": False,
            "error": "Only read-only SELECT queries are allowed."
        }

    try:

        connection = sqlite3.connect(DB_PATH)
        connection.row_factory = sqlite3.Row

        cursor = connection.cursor()
        cursor.execute(sql)

        rows = cursor.fetchall()

        columns = [
            description[0]
            for description in cursor.description
        ]

        data = [dict(row) for row in rows]

        connection.close()

        return {
            "success": True,
            "columns": columns,
            "rows": data,
            "row_count": len(data)
        }

    except Exception as error:

        return {
            "success": False,
            "error": str(error)
        }


# ============================================================
# CHART GENERATION
# ============================================================

def generate_chart(
    data: dict[str, Any],
    chart_type: str = "bar",
    title: str = "Data Visualization"
) -> dict[str, Any]:
    """
    Generate a chart from query results.

    Supported chart types:
    bar, line, pie, scatter
    """

    if not data.get("success"):
        return {
            "success": False,
            "error": data.get("error", "Invalid data")
        }

    rows = data.get("rows", [])
    columns = data.get("columns", [])

    if not rows:
        return {
            "success": False,
            "error": "No data available for visualization."
        }

    if len(columns) < 2:
        return {
            "success": False,
            "error": "At least two columns are required for a chart."
        }

    try:
        CHART_DIR.mkdir(parents=True, exist_ok=True)

        # Automatically detect categorical and numeric columns
        numeric_columns = []
        categorical_columns = []

        for column in columns:
            values = [row.get(column) for row in rows]

            non_none_values = [
                value for value in values
                if value is not None
            ]

            if non_none_values and all(
                isinstance(value, (int, float))
                and not isinstance(value, bool)
                for value in non_none_values
            ):
                numeric_columns.append(column)
            else:
                categorical_columns.append(column)

        if not numeric_columns or not categorical_columns:
            return {
                "success": False,
                "error": "Could not automatically determine chart columns."
            }

        x_column = categorical_columns[0]
        y_column = numeric_columns[-1]

        if chart_type == "bar":
            figure = px.bar(
                rows,
                x=x_column,
                y=y_column,
                title=title
            )

        elif chart_type == "line":
            figure = px.line(
                rows,
                x=x_column,
                y=y_column,
                title=title,
                markers=True
            )

        elif chart_type == "pie":
            figure = px.pie(
                rows,
                names=x_column,
                values=y_column,
                title=title
            )

        elif chart_type == "scatter":
            figure = px.scatter(
                rows,
                x=x_column,
                y=y_column,
                title=title
            )

        else:
            return {
                "success": False,
                "error": (
                    "Unsupported chart type. "
                    "Use bar, line, pie, or scatter."
                )
            }

        chart_id = f"chart_{abs(hash(title))}.html"
        chart_path = CHART_DIR / chart_id

        figure.write_html(
            str(chart_path),
            include_plotlyjs="cdn"
        )

        return {
            "success": True,
            "chart_type": chart_type,
            "title": title,
            "url": f"/charts/{chart_id}"
        }

    except Exception as error:
        return {
            "success": False,
            "error": str(error)
        }


# ============================================================
# DATA EXPLANATION
# ============================================================

def explain_data(data: dict[str, Any]) -> str:
    """Generate a useful natural-language explanation."""

    if not data.get("success"):
        return f"Unable to analyze the data: {data.get('error')}"

    rows = data.get("rows", [])

    if not rows:
        return "The query returned no results."

    columns = data.get("columns", [])

    explanation = (
        f"The query returned {len(rows)} result"
        f"{'s' if len(rows) != 1 else ''}. "
        f"The result contains the columns: "
        f"{', '.join(columns)}."
    )

    # Find a numeric column instead of assuming
    # that the second column contains the value.
    numeric_column = None

    for column in columns:
        values = [
            row.get(column)
            for row in rows
            if isinstance(row.get(column), (int, float))
        ]

        if values:
            # Prefer revenue/value-like columns
            if any(word in column.lower() for word in [
                "revenue",
                "sales",
                "amount",
                "total",
                "price",
                "value"
            ]):
                numeric_column = column
                break

    # If no value-like column was found, use a numeric column
    if numeric_column is None:
        for column in columns:
            if any(
                isinstance(row.get(column), (int, float))
                for row in rows
            ):
                numeric_column = column
                break

    if numeric_column:
        valid_rows = [
            row for row in rows
            if isinstance(row.get(numeric_column), (int, float))
        ]

        if valid_rows:
            highest_row = max(
                valid_rows,
                key=lambda row: row.get(numeric_column)
            )

            # Find a useful label column
            label_column = None

            for column in columns:
                if column != numeric_column:
                    value = highest_row.get(column)

                    if isinstance(value, str):
                        label_column = column
                        break

            if label_column:
                explanation += (
                    f" The highest {numeric_column} is "
                    f"{highest_row.get(numeric_column)} "
                    f"for {highest_row.get(label_column)}."
                )
            else:
                explanation += (
                    f" The highest {numeric_column} is "
                    f"{highest_row.get(numeric_column)}."
                )

    return explanation

    # --------------------------------------------------------
    # Find highest numeric value
    # --------------------------------------------------------

    for column in columns:

        values = [
            row.get(column)
            for row in rows
            if isinstance(
                row.get(column),
                (int, float)
            )
            and not isinstance(
                row.get(column),
                bool
            )
        ]

        if values:

            highest_value = max(values)

            highest_row = next(
                row
                for row in rows
                if row.get(column) == highest_value
            )

            # Find a useful label column
            label = None

            for other_column in columns:

                if other_column != column:

                    value = highest_row.get(other_column)

                    if isinstance(value, str):

                        label = value
                        break

            if label is not None:

                explanation += (
                    f" The highest value is "
                    f"{highest_value} for {label}."
                )

            else:

                explanation += (
                    f" The highest value is "
                    f"{highest_value}."
                )

            break

    return explanation


# ============================================================
# ER DIAGRAM GENERATION
# ============================================================

def generate_flowchart(
    schema: dict[str, Any]
) -> dict[str, Any]:
    """Generate a rendered Mermaid ER diagram."""

    tables = schema.get("tables", {})
    relationships = schema.get("relationships", [])

    if not tables:

        return {
            "success": False,
            "error": "No database tables found."
        }

    try:

        CHART_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        lines = ["erDiagram"]

        # ----------------------------------------------------
        # Add tables
        # ----------------------------------------------------

        for table_name, table_info in tables.items():

            lines.append(
                f"    {table_name} {{"
            )

            for column in table_info["columns"]:

                column_type = column["type"].lower()
                column_name = column["name"]

                if column["primary_key"]:

                    lines.append(
                        f"        {column_type} "
                        f"{column_name} PK"
                    )

                else:

                    lines.append(
                        f"        {column_type} "
                        f"{column_name}"
                    )

            lines.append("    }")

        # ----------------------------------------------------
        # Add relationships
        # ----------------------------------------------------

        for relationship in relationships:

            from_table = relationship["from_table"]
            to_table = relationship["to_table"]

            lines.append(
                f"    {to_table} ||--o{{ "
                f"{from_table} : contains"
            )

        mermaid_code = "\n".join(lines)

        # ----------------------------------------------------
        # Save diagram
        # ----------------------------------------------------

        diagram_id = (
            f"er_diagram_"
            f"{abs(hash(mermaid_code))}.html"
        )

        diagram_path = CHART_DIR / diagram_id

        html = f"""
<!DOCTYPE html>

<html>

<head>

    <meta charset="UTF-8">

    <title>
        Database ER Diagram
    </title>

    <script type="module">

        import mermaid from
        "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";

        mermaid.initialize({{
            startOnLoad: true,
            theme: "default"
        }});

    </script>

    <style>

        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 30px;
            background: #f5f7fb;
        }}

        h1 {{
            text-align: center;
        }}

        .diagram {{
            background: white;
            padding: 30px;
            border-radius: 15px;
            overflow-x: auto;
        }}

    </style>

</head>

<body>

<h1>
    Database ER Diagram
</h1>

<div class="diagram">

    <div class="mermaid">

{mermaid_code}

    </div>

</div>

</body>

</html>
"""

        diagram_path.write_text(
            html,
            encoding="utf-8"
        )

        return {
            "success": True,
            "diagram_type": "ER",
            "title": "Database Entity Relationship Diagram",
            "url": f"/charts/{diagram_id}",
            "mermaid": mermaid_code
        }

    except Exception as error:

        return {
            "success": False,
            "error": str(error)
        }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("\n=== DATABASE SCHEMA ===")

    schema = get_schema()

    print(schema)

    print("\n=== TEST QUERY ===")

    result = execute_query("""
        SELECT
            p.name AS product,
            SUM(
                oi.quantity * p.price
            ) AS revenue
        FROM order_items oi
        JOIN products p
            ON oi.product_id = p.product_id
        GROUP BY p.product_id
        ORDER BY revenue DESC
        LIMIT 5
    """)

    print(result)

    print("\n=== EXPLANATION ===")

    print(
        explain_data(result)
    )

    print("\n=== CHART ===")

    chart = generate_chart(
        result,
        chart_type="bar",
        title="Top 5 Products by Revenue"
    )

    print(chart)

    print("\n=== ER DIAGRAM ===")

    diagram = generate_flowchart(schema)

    print(diagram)