import pandas as pd
import random
import string

random.seed(42)

departments = ["Sales", "Engineering", "HR", "Marketing", "Finance"]
job_roles = {
    "Sales": ["Sales Rep", "Account Manager", "Sales Director"],
    "Engineering": ["Junior Developer", "Senior Developer", "Tech Lead", "Engineering Manager"],
    "HR": ["HR Specialist", "HR Coordinator", "HR Manager"],
    "Marketing": ["Marketing Specialist", "Content Creator", "Marketing Manager"],
    "Finance": ["Accountant", "Financial Analyst", "Finance Manager"]
}
genders = ["Male", "Female", "Non-binary", "Prefer not to say"]

first_names = ["James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda", "David", "Elizabeth", "William", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Lisa", "Daniel", "Nancy", "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra"]
last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]

def generate_employee_id():
    return f"EMP{''.join(random.choices(string.digits, k=5))}"

def generate_name():
    return f"{random.choice(first_names)} {random.choice(last_names)}"

def generate_age():
    return random.randint(22, 60)

def generate_department():
    return random.choice(departments)

def generate_job_role(department):
    return random.choice(job_roles[department])

def generate_salary(job_role):
    base_salaries = {
        "Junior Developer": 50000,
        "Senior Developer": 85000,
        "Tech Lead": 110000,
        "Engineering Manager": 130000,
        "Sales Rep": 45000,
        "Account Manager": 65000,
        "Sales Director": 120000,
        "HR Specialist": 50000,
        "HR Coordinator": 55000,
        "HR Manager": 95000,
        "Marketing Specialist": 52000,
        "Content Creator": 48000,
        "Marketing Manager": 90000,
        "Accountant": 58000,
        "Financial Analyst": 68000,
        "Finance Manager": 100000
    }
    base = base_salaries.get(job_role, 60000)
    return int(base + random.gauss(0, base * 0.15))

def generate_years_at_company():
    return random.randint(0, 25)

def generate_satisfaction_score():
    return round(random.uniform(1.0, 5.0), 1)

def generate_overtime_hours():
    return random.randint(0, 40)

def generate_performance_rating():
    return random.randint(1, 5)

def generate_attrition(years_at_company, satisfaction_score, performance_rating):
    score = years_at_company * 0.5 + satisfaction_score * 2 + performance_rating * 3
    return "Yes" if score < 12 and random.random() < 0.15 else "No"

employees = []
for i in range(1000):
    department = generate_department()
    job_role = generate_job_role(department)
    years_at_company = generate_years_at_company()
    satisfaction_score = generate_satisfaction_score()
    performance_rating = generate_performance_rating()
    
    employees.append({
        "employee_id": generate_employee_id(),
        "name": generate_name(),
        "age": generate_age(),
        "gender": random.choice(genders),
        "department": department,
        "job_role": job_role,
        "salary": generate_salary(job_role),
        "years_at_company": years_at_company,
        "satisfaction_score": satisfaction_score,
        "overtime_hours": generate_overtime_hours(),
        "performance_rating": performance_rating,
        "attrition": generate_attrition(years_at_company, satisfaction_score, performance_rating)
    })

df = pd.DataFrame(employees)
df.to_csv("sample_data/employees.csv", index=False)
print(f"Generated {len(df)} employee records to sample_data/employees.csv")
