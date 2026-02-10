import google.generativeai as genai
import json
import os
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

def analyze_data(profile_json):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in .env file")
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash-exp")
    
    prompt = f"""You are a senior data analyst. I will give you a data profile (schema, statistics, sample rows) of a CSV dataset.

Your job:
1. Identify what this dataset represents (domain, purpose)
2. List the 4-5 most interesting analytical questions this data can answer
3. For each question, specify:
   - The exact columns to use
   - The type of analysis (correlation, distribution, comparison, trend, anomaly detection)
   - The best chart type (bar, scatter, histogram, box, heatmap, line, violin, pie)
   - A short description of what insight to look for
4. Identify any data cleaning steps needed (handle missing values, outliers, type conversions)

Return your response as ONLY valid JSON with this structure:
{{
  "dataset_description": "string",
  "cleaning_steps": ["step1", "step2"],
  "analyses": [
    {{
      "question": "string",
      "columns": ["col1", "col2"],
      "analysis_type": "string",
      "chart_type": "string",
      "insight_hint": "string"
    }}
  ]
}}

Here is the data profile:
{json.dumps(profile_json)}
"""
    
    response = model.generate_content(prompt)
    json_text = extract_json_from_response(response)
    return json.loads(json_text)

def narrate_results(analysis_results):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in .env file")
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash-exp")
    
    prompt = f"""You are a senior data analyst writing a report for stakeholders.

I will give you the raw results of a data analysis (statistical findings, chart descriptions, detected patterns).

Write:
1. An executive summary (3-4 sentences, the most important takeaway)
2. Key findings (bullet points, one per analysis performed)
3. Recommendations (2-3 actionable next steps based on the data)

Return your response as ONLY valid JSON:
{{
  "executive_summary": "string",
  "key_findings": ["finding1", "finding2"],
  "recommendations": ["rec1", "rec2"]
}}

Here are the analysis results:
{json.dumps(analysis_results)}
"""
    
    response = model.generate_content(prompt)
    json_text = extract_json_from_response(response)
    return json.loads(json_text)

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
