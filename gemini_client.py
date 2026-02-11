import google.genai as genai
import json
import os
import time
from dotenv import load_dotenv

load_dotenv()

def extract_json_from_response(response):
    text = response.text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()

def analyze_data_with_gemini(profile_json):
    """Analyze data using Gemini API."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY or GOOGLE_GEMINI_API_KEY not found in .env file")

    client = genai.Client(api_key=api_key)

    prompt = """You are a senior data analyst. I will give you a data profile (schema, statistics, sample rows) of a CSV dataset.

Your job:
1. Identify what this dataset represents (domain, purpose)
2. List the 4-5 most interesting analytical questions this data can answer
3. For each question, specify:
   - The exact columns to use
   - The type of analysis (correlation, distribution, comparison, trend, anomaly detection)
   - The best chart type (bar, scatter, histogram, box, heatmap, line, violin, pie)
   - A short description of what insight to look for
4. Identify data cleaning steps needed with SPECIFIC handling for null values and edge cases:
   - For each column with null values, specify: "Drop rows with null in [column_name]" OR "Fill null in [column_name] with [value/mode/median/mean]"
   - For numeric columns: use mean, median, or a specific value
   - For categorical columns: use mode or "Unknown"
   - For columns with string patterns (like duration "2h 30m" or stops "2 stops"), handle edge cases like "non-stop" or empty strings
   - NEVER use operations that assume non-null values (like .split()) without first handling nulls and edge cases
   - Add a check: if converting strings to numeric, handle parsing errors with try-except or pd.to_numeric with errors='coerce'

IMPORTANT: If any column has null values, you MUST include explicit null-handling steps in cleaning_steps before any other operations.

Return your response as ONLY valid JSON with this structure:
{
  "dataset_description": "string",
  "cleaning_steps": ["step1", "step2"],
  "analyses": [
    {
      "question": "string",
      "columns": ["col1", "col2"],
      "analysis_type": "string",
      "chart_type": "string",
      "insight_hint": "string"
    }
  ]
}

Here is the data profile:
""" + json.dumps(profile_json)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    json_text = extract_json_from_response(response)
    return json.loads(json_text)

def analyze_data_with_groq(profile_json):
    """Analyze data using Groq API as fallback."""
    from groq import Groq
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in .env file")

    client = Groq(api_key=api_key)

    prompt = f"""You are a senior data analyst. Analyze this dataset and generate an analysis plan.

DATA PROFILE:
{json.dumps(profile_json, indent=2)}

Return ONLY valid JSON:
{{
  "dataset_description": "What this dataset represents",
  "cleaning_steps": ["list of data cleaning operations needed"],
  "analyses": [
    {{
      "question": "Analytical question to answer",
      "columns": ["column1", "column2"],
      "analysis_type": "distribution/comparison/correlation/trend",
      "chart_type": "bar/scatter/histogram/box/heatmap/line",
      "insight_hint": "What insight to look for"
    }}
  ]
}}

Make sure to handle null values and edge cases in cleaning_steps.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a senior data analyst. Always return valid JSON only."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    text = response.choices[0].message.content.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    
    return json.loads(text.strip())

def analyze_data(profile_json):
    """Analyze data with Gemini, fall back to Groq if quota exceeded."""
    try:
        return analyze_data_with_gemini(profile_json)
    except Exception as e:
        error_str = str(e)
        if "RESOURCE_EXHAUSTED" in error_str or "429" in error_str:
            return analyze_data_with_groq(profile_json)
        raise

def narrate_results_with_gemini(analysis_results):
    """Narrate results using Gemini API."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY or GOOGLE_GEMINI_API_KEY not found in .env file")

    client = genai.Client(api_key=api_key)

    prompt = """You are a senior data analyst writing a report for stakeholders.

I will give you the raw results of a data analysis (statistical findings, chart descriptions, detected patterns).

Write:
1. An executive summary (3-4 sentences, the most important takeaway)
2. Key findings (bullet points, one per analysis performed)
3. Recommendations (2-3 actionable next steps based on the data)

Return your response as ONLY valid JSON:
{
  "executive_summary": "string",
  "key_findings": ["finding1", "finding2"],
  "recommendations": ["rec1", "rec2"]
}

Here are the analysis results:
""" + json.dumps(analysis_results)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    json_text = extract_json_from_response(response)
    return json.loads(json_text)

def narrate_results_with_groq(analysis_results):
    """Narrate results using Groq API as fallback."""
    from groq import Groq
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in .env file")

    client = Groq(api_key=api_key)

    prompt = f"""You are a senior data analyst. Write a report based on these analysis results.

ANALYSIS RESULTS:
{json.dumps(analysis_results, indent=2)}

Return ONLY valid JSON:
{{
  "executive_summary": "3-4 sentence summary of key findings",
  "key_findings": ["finding 1", "finding 2", "finding 3"],
  "recommendations": ["recommendation 1", "recommendation 2"]
}}

Be concise and actionable.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a senior data analyst. Always return valid JSON only."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    text = response.choices[0].message.content.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    
    return json.loads(text.strip())

def narrate_results(analysis_results):
    """Narrate results with Gemini, fall back to Groq if quota exceeded."""
    try:
        return narrate_results_with_gemini(analysis_results)
    except Exception as e:
        error_str = str(e)
        if "RESOURCE_EXHAUSTED" in error_str or "429" in error_str:
            return narrate_results_with_groq(analysis_results)
        raise

if __name__ == "__main__":
    import sys
    from profiler import profile_csv

    if len(sys.argv) < 2:
        print("Usage: python gemini_client.py <csv_file>")
        sys.exit(1)

    profile = profile_csv(sys.argv[1])
    print("Testing analyze_data...")
    plan = analyze_data(profile)
    print(json.dumps(plan, indent=2))
