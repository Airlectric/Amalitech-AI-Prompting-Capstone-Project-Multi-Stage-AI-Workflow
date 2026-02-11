import json
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def extract_code_from_response(response):
    text = response.choices[0].message.content.strip()
    if text.startswith("```python"):
        text = text[9:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()

def post_process_code(code):
    lines = code.split('\n')
    processed_lines = []
    for line in lines:
        if 'plt.show()' in line:
            continue
        processed_lines.append(line)
    return '\n'.join(processed_lines)

def generate_code(data_profile, analysis_plan):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in .env file")
    
    client = Groq(api_key=api_key)
    
    prompt = f"""You are an expert Python data analyst. Generate a COMPLETE, RUNNABLE Python script that performs the following analysis on a CSV file.

RULES:
- The CSV file path will be passed as the first command-line argument (sys.argv[1])
- Use only: pandas, matplotlib, seaborn, sys, os
- Save each chart as a PNG file in an "output/charts/" directory (create it if it doesn't exist)
- Print a JSON object to stdout with the key results of each analysis
- Do NOT use plt.show() — only plt.savefig()
- Handle errors gracefully
- Close each figure after saving to avoid memory issues

CRITICAL NULL HANDLING - USE EXACT SYNTAX:
- ALWAYS handle null values BEFORE applying any string operations (like .split())
- For numeric columns with nulls: use df.loc[:, 'column_name'] = df['column_name'].fillna(df['column_name'].median())
- For categorical columns with nulls: use df.loc[:, 'column_name'] = df['column_name'].fillna("Unknown")
- IMPORTANT: Use df.loc[:, 'col'] = df['col'].fillna(value) NOT df['col'].fillna(value, inplace=True)
- Handle NaN values in string columns BEFORE calling .split() - check for NaN and replace with a default value first using the correct syntax above
- Check for nulls using df.isnull().sum() and handle them explicitly

DATA SCHEMA:
{json.dumps(data_profile, indent=2)}

ANALYSIS PLAN:
{json.dumps(analysis_plan, indent=2)}

Return ONLY the Python code, no markdown fences, no explanation.
"""
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are an expert Python data analyst."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )
    
    code = extract_code_from_response(response)
    code = post_process_code(code)
    return code

if __name__ == "__main__":
    import sys
    from profiler import profile_csv
    
    if len(sys.argv) < 2:
        print("Usage: python groq_client.py <csv_file>")
        sys.exit(1)
    
    print("Generating sample profile for testing...")
    profile = profile_csv(sys.argv[1])
    
    print("Testing generate_code...")
    code = generate_code(profile, {
        "dataset_description": "Employee dataset",
        "cleaning_steps": [],
        "analyses": [
            {
                "question": "What is the salary distribution by department?",
                "columns": ["department", "salary"],
                "analysis_type": "distribution",
                "chart_type": "box",
                "insight_hint": "Compare salary ranges across departments"
            }
        ]
    })
    print("Generated code:")
    print(code)
