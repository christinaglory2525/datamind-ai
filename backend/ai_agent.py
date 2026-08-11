from backend.query_engine import search_employees


def run_agent(question):

    question = question.lower()

    if "ai department" in question:
        return search_employees(
            department="AI"
        )

    elif "salary above 90000" in question:
        return search_employees(
            min_salary=90000
        )

    else:
        return {
            "message": "I could not understand the query"
        }