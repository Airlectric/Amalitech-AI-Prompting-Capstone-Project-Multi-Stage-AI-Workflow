import json
import os
from dotenv import load_dotenv

load_dotenv()

def extract_code_from_text(text):
    text = text.strip()
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

def _build_prompt(data_profile, analysis_plan):
    return f"""You are an expert Python data analyst. Generate a COMPLETE, RUNNABLE Python script that performs the following analysis on a CSV file.

RULES:
- The CSV file path will be passed as the first command-line argument (sys.argv[1])
- Use only: pandas, matplotlib, seaborn, sys, os, re
- Save each chart as a PNG file in an "output/charts/" directory (create it if it doesn't exist)
- IMPORTANT: Name chart files using simple numbered names ONLY, like "chart_1.png", "chart_2.png", etc. Do NOT use question text, special characters, or spaces in filenames. Example: plt.savefig("output/charts/chart_1.png")
- Print a JSON object to stdout with the key results of each analysis
- Do NOT use plt.show() — only plt.savefig()
- CRITICAL ERROR HANDLING: Wrap EACH individual analysis in its own try/except block so that if one analysis fails, the script continues to the next. Print any errors to stderr but do NOT re-raise them. The script must always reach the end and print the JSON results to stdout.
- Close each figure after saving with plt.close() to avoid memory issues

CRITICAL DATA TYPE HANDLING - USE EXACT SYNTAX:
1. For null handling: df.loc[:, 'column_name'] = df['column_name'].fillna(value)
2. For converting categorical string columns to numeric:
   - Create a mapping dictionary: mapping = {{'value1': 1, 'value2': 2}}
   - Apply the mapping: df['column_name'] = df['column_name'].map(mapping)
   - Convert to numeric: df['column_name'] = pd.to_numeric(df['column_name'], errors='coerce')
   - Fill NaN: df['column_name'] = df['column_name'].fillna(df['column_name'].median())
   - Convert to integer: df['column_name'] = df['column_name'].astype(int)
3. For datetime conversion - USE DIRECT ASSIGNMENT, NOT loc:
   - First convert to datetime: df['column_name'] = pd.to_datetime(df['column_name'], format='mixed', dayfirst=True)
   - This automatically updates the column in place without needing loc
4. For string operations like .split(), ALWAYS handle NaN first using fillna
5. For Duration parsing (e.g., "2h 30m", "30m", "5h"):
   - First fill NaN: df['Duration'] = df['Duration'].fillna('0m')
   - Use a robust function that handles all formats:
     def parse_duration(d):
         d = str(d).strip()
         hours = 0
         minutes = 0
         if 'h' in d:
             parts = d.split('h')
             if parts[0].strip():
                 try:
                     hours = int(parts[0].strip())
                 except:
                     hours = 0
             if len(parts) > 1 and 'm' in parts[1]:
                 try:
                     minutes = int(parts[1].split('m')[0].strip())
                 except:
                     minutes = 0
         elif 'm' in d:
             try:
                 minutes = int(d.split('m')[0].strip())
             except:
                 minutes = 0
         return hours * 60 + minutes
   - Apply: df['Duration_Minutes'] = df['Duration'].apply(parse_duration)
6. Always verify column types after conversion using df.dtypes

DATA SCHEMA:
{json.dumps(data_profile, indent=2)}

ANALYSIS PLAN:
{json.dumps(analysis_plan, indent=2)}

Return ONLY the Python code, no markdown fences, no explanation.
"""

def generate_code_with_groq(data_profile, analysis_plan):
    """Generate code using Groq API."""
    from groq import Groq

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in .env file")

    client = Groq(api_key=api_key)
    prompt = _build_prompt(data_profile, analysis_plan)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are an expert Python data analyst."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    return extract_code_from_text(response.choices[0].message.content)

def generate_code_with_cerebras(data_profile, analysis_plan):
    """Generate code using Cerebras API as fallback."""
    try:
        from cerebras.cloud.sdk import Cerebras
    except ImportError:
        raise ValueError("cerebras-cloud-sdk not found. Make sure you're using the venv Python: 'venv\\Scripts\\python.exe -m streamlit run app.py'")

    api_key = os.getenv("CEREBRAS_API_KEY")
    if not api_key:
        raise ValueError("CEREBRAS_API_KEY not found in .env file")

    client = Cerebras(api_key=api_key)
    prompt = _build_prompt(data_profile, analysis_plan)

    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are an expert Python data analyst."},
            {"role": "user", "content": prompt}
        ],
        model="llama-3.3-70b",
        max_completion_tokens=8192,
        temperature=0.2
    )

    return extract_code_from_text(response.choices[0].message.content)


def generate_code(data_profile, analysis_plan):
    """Generate code with Groq, fall back to Cerebras."""
    apis = [
        ("Groq", generate_code_with_groq),
        ("Cerebras", generate_code_with_cerebras)
    ]

    last_error = None
    for api_name, api_func in apis:
        try:
            code = api_func(data_profile, analysis_plan)
            return post_process_code(code)
        except ImportError as e:
            last_error = e
            continue
        except Exception as e:
            error_str = str(e)
            last_error = e

            if "RESOURCE_EXHAUSTED" in error_str or "429" in error_str or "quota" in error_str.lower() or "rate_limit" in error_str.lower():
                continue
            elif "not found" in error_str.lower() or "invalid" in error_str.lower() or "authentication" in error_str.lower():
                continue
            else:
                raise

    raise ValueError(f"All APIs failed. Last error: {str(last_error)}")

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
