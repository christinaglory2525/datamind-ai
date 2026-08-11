from backend.database import Base, engine, SessionLocal
from backend.models import Employee
Base.metadata.create_all(bind=engine)

db = SessionLocal()

if db.query(Employee).count() == 0:
    employees = [
        Employee(name="Alice", department="AI", salary=80000, experience=3),
        Employee(name="Bob", department="HR", salary=50000, experience=5),
        Employee(name="Charlie", department="Finance", salary=90000, experience=7),
        Employee(name="David", department="AI", salary=95000, experience=6),
        Employee(name="Eva", department="Marketing", salary=60000, experience=2),
    ]

    db.add_all(employees)
    db.commit()

db.close()

print("Database created successfully!")