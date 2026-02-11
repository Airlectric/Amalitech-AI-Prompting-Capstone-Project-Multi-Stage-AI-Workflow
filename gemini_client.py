import google.genai as genai
import json
import os
import time
from dotenv import load_dotenv

load_dotenv()

API_COOLDOWN_SECONDS = 3

LAST_API_CALL_TIME = 0

def extract_json_from_response(response):
    text = response.text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()

def rate_limit():
    global LAST_API_CALL_TIME
    elapsed = time.time() - LAST_API_CALL_TIME
    if elapsed < API_COOLDOWN_SECONDS:
        time.sleep(API_COOLDOWN_SECONDS - elapsed)
    LAST_API_CALL_TIME = time.time()

def analyze_data(profile_json, max_retries=3):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY or GOOGLE_GEMINI_API_KEY not found in .env file")

    models_to_try = ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
    last_error = None
    
    for attempt in range(max_retries):
        for model in models_to_try:
            try:
                rate_limit()
                
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
                    model=model,
                    contents=prompt
                )
                json_text = extract_json_from_response(response)
                return json.loads(json_text)
                
            except Exception as e:
                error_str = str(e)
                last_error = e
                
                if "RESOURCE_EXHAUSTED" in error_str or "429" in error_str:
                    wait_time = 60
                    if "retry in" in error_str.lower():
                        try:
                            import re
                            match = re.search(r'retry in ([\d.]+)s', error_str.lower())
                            if match:
                                wait_time = float(match.group(1)) + 5
                        except:
                            pass
                    
                    if attempt < max_retries - 1:
                        time.sleep(wait_time)
                        continue
                break
        
        if attempt < max_retries - 1:
            time.sleep(60)
    
    raise ValueError(f"Failed after {max_retries} retries. Last error: {str(last_error)}")

def narrate_results(analysis_results, max_retries=3):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY or GOOGLE_GEMINI_API_KEY not found in .env file")

    models_to_try = ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
    last_error = None
    
    for attempt in range(max_retries):
        for model in models_to_try:
            try:
                rate_limit()
                
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
                    model=model,
                    contents=prompt
                )
                json_text = extract_json_from_response(response)
                return json.loads(json_text)
                
            except Exception as e:
                error_str = str(e)
                last_error = e
                
                if "RESOURCE_EXHAUSTED" in error_str or "429" in error_str:
                    wait_time = 60
                    if "retry in" in error_str.lower():
                        try:
                            import re
                            match = re.search(r'retry in ([\d.]+)s', error_str.lower())
                            if match:
                                wait_time = float(match.group(1)) + 5
                        except:
                            pass
                    
                    if attempt < max_retries - 1:
                        time.sleep(wait_time)
                        continue
                break
        
        if attempt < max_retries - 1:
            time.sleep(60)
    
    raise ValueError(f"Failed after {max_retries} retries. Last error: {str(last_error)}")

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
