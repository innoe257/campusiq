import pandas as pd
import numpy as np
from datetime import datetime
import random
import os

def generate_synthetic_data(n_students: int = 1000, output_path: str = "data/synthetic_students.csv") -> pd.DataFrame:
    """Generate synthetic student data for the attrition prediction model."""
    
    random.seed(42)
    np.random.seed(42)
    
    programs = ["Computer Science", "Business", "Psychology", "Engineering", "Nursing", "Biology", "Mathematics"]
    majors = {
        "Computer Science": ["Software Engineering", "Data Science", "AI/ML", "Cybersecurity"],
        "Business": ["Finance", "Marketing", "Management", "Accounting"],
        "Psychology": ["Clinical Psychology", "Counseling", "Research", "Forensic"],
        "Engineering": ["Mechanical", "Electrical", "Civil", "Chemical"],
        "Nursing": ["RN Program", "BSN", "Nurse Practitioner"],
        "Biology": ["Molecular Biology", "Ecology", "Pre-Med", "Marine Biology"],
        "Mathematics": ["Applied Math", "Statistics", "Actuarial Science"],
    }
    
    data = []
    for i in range(n_students):
        program = random.choice(programs)
        major = random.choice(majors[program])
        enrollment_year = random.randint(2020, 2024)
        
        # Generate base features
        gpa = np.random.normal(3.0, 0.6)
        gpa = max(0.0, min(4.0, gpa))
        
        attendance_rate = np.random.beta(8, 2) if gpa > 2.5 else np.random.beta(4, 4)
        engagement_score = np.random.beta(7, 3) if gpa > 2.5 else np.random.beta(3, 5)
        
        credits_attempted = random.randint(12, 120)
        completion_rate = np.random.beta(8, 2) if gpa > 2.5 else np.random.beta(3, 5)
        credits_earned = int(credits_attempted * completion_rate)
        
        financial_aid = random.random() < 0.45
        first_generation = random.random() < 0.25
        age = random.randint(18, 35)
        
        first_semester_gpa = gpa + np.random.normal(0, 0.3)
        first_semester_gpa = max(0.0, min(4.0, first_semester_gpa))
        
        # Determine dropout based on features (with some noise)
        dropout_risk = (
            0.3 * (1 - gpa / 4.0) +
            0.2 * (1 - attendance_rate) +
            0.2 * (1 - engagement_score) +
            0.1 * (1 if financial_aid else 0) +
            0.1 * (1 if first_generation else 0) +
            0.1 * (1 - completion_rate)
        )
        dropped_out = random.random() < dropout_risk
        
        data.append({
            "student_id": f"STU-{enrollment_year}-{i+1:04d}",
            "first_name": f"Student_{i+1}",
            "last_name": f"Lastname_{i+1}",
            "email": f"student_{i+1}@uni.edu",
            "enrollment_year": enrollment_year,
            "program": program,
            "major": major,
            "current_gpa": round(gpa, 2),
            "first_semester_gpa": round(first_semester_gpa, 2),
            "credits_earned": credits_earned,
            "credits_attempted": credits_attempted,
            "attendance_rate": round(attendance_rate, 2),
            "engagement_score": round(engagement_score, 2),
            "financial_aid": financial_aid,
            "first_generation": first_generation,
            "age": age,
            "dropped_out": int(dropped_out),
        })
    
    df = pd.DataFrame(data)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Generated {n_students} synthetic student records at {output_path}")
    
    return df

if __name__ == "__main__":
    generate_synthetic_data()
