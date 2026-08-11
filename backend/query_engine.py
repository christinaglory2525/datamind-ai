from backend.database import SessionLocal
from backend.models import Employee


def search_employees(department=None, min_salary=None):

    db = SessionLocal()

    query = db.query(Employee)

    if department:
        query = query.filter(
            Employee.department == department
        )

    if min_salary:
        query = query.filter(
            Employee.salary >= min_salary
        )

    employees = query.all()

    result = []

    for emp in employees:
        result.append({
            "name": emp.name,
            "department": emp.department,
            "salary": emp.salary,
            "experience": emp.experience
        })

    db.close()

    return result