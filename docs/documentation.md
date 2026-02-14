# Automated Intelligent Data Analysis Pipeline

## Documentation

---

## 1. Problem Statement

Data analysis is a critical but time-consuming process. When a data analyst receives a raw CSV file, they must manually:
- Understand the data structure and schema
- Clean and preprocess the data
- Explore distributions and relationships
- Detect patterns and anomalies
- Choose appropriate visualizations
- Generate charts and graphs
- Write a comprehensive summary report

This manual process typically takes **2–4 hours of skilled human work per dataset**. For organizations handling multiple datasets daily, this represents a significant bottleneck in decision-making workflows.

---

## 2. Solution Overview

Our **Automated Intelligent Data Analysis Pipeline** transforms a raw CSV file into a complete, professional HTML report in under **60 seconds** with zero human intervention.

The solution chains **two different AI tools via API**:
1. **Gemini API** (Google) - Acts as the data analyst and report narrator
2. **Groq API** (Llama 3.3) - Generates executable Python analysis code

A single command (`python pipeline.py dataset.csv`) orchestrates all 6 stages, from data profiling to final report generation.

---

## 3. Tools Used

| Tool | Provider | UX Type | Role in Pipeline | Cost |
|------|----------|---------|------------------|------|
| **Gemini API** (gemini-2.5-flash) | Google | Chat AI | Data Analyst (Stage 1) + Report Narrator (Stage 4) | Free tier |
| **Groq API** (llama-3.3-70b-versatile) | Groq | Code Gen AI | Python Code Generator (Stage 2) | Free tier |
| **Cerebras API** (llama-3.3-70b) | Cerebras | Code Gen AI | Fallback for Stage 2 | Free tier |
| **OpenRouter** (deepseek-chat-v3-0324) | OpenRouter | Chat AI | Fallback for Stages 1 & 4 | Free tier |
| **Python** | - | CLI + Streamlit | Profiling, Execution, Compilation (Stages 0, 3, 5) | Free |

---

## 4. Workflow Steps

![Pipeline Workflow Diagram](../Workflow%20Diagram/AI_Workflow.png)

### Stage 0: Data Profiling (Python)
- Reads the CSV file with pandas
- For large datasets (over 2,000 rows), statistics are computed on a random sample of 2,000 rows to keep the profile compact; the full dataset is still used in Stage 3
- Extracts schema: column names, data types, row count
- Calculates statistics: mean, median, min, max, std, skewness, kurtosis, percentiles for numeric columns
- Counts missing values per column, top value counts for categorical columns
- Samples 3 representative rows
- **Output:** `data_profile` (JSON)

### Stage 1: AI Analysis Planning (Gemini API)
- Receives the data profile
- Identifies what the dataset represents
- Generates 4-5 analytical questions to answer
- Specifies columns, analysis types, and chart types for each
- Suggests data cleaning steps
- **Output:** `analysis_plan` (JSON)

### Stage 2: Code Generation (Groq API)
- Receives data profile and analysis plan
- Generates a complete, runnable Python script
- Script handles: data loading, cleaning, analysis, chart generation
- **Output:** `analysis_script.py` (Python code string)

### Stage 3: Auto-Execution (Python)
- Clears old charts from previous runs to avoid stale results
- Writes generated code to a file
- Executes via subprocess with 120-second timeout
- Captures stdout (analysis results) and stderr (errors)
- Collects generated PNG charts
- If the script crashes partway through but some charts were already saved, the pipeline treats it as a partial success and continues
- **Output:** `charts` (PNG files) + `raw_insights` (JSON)

### Stage 4: Narrative Generation (Gemini API)
- Receives raw analysis results and chart descriptions
- Writes an executive summary (3-4 sentences)
- Generates key findings (bullet points)
- Provides actionable recommendations
- **Output:** `narrative` (JSON)

### Stage 5: Report Compilation (Python)
- Loads Jinja2 HTML template
- Embeds charts as base64 data URIs
- Injects narrative, findings, recommendations
- Adds metadata (dataset name, timestamp, tools used)
- **Output:** `report.html` (self-contained HTML file)

---

## 5. Final Prompts

### Prompt 1: The Analyst (Stage 1 - Gemini API)

```
You are a senior data analyst. I will give you a data profile (schema, statistics, sample rows) of a CSV dataset.

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
   - For columns with string patterns (like duration "2h 30m", "30m", "5h" or stops "2 stops"), handle ALL edge cases
   - ALWAYS specify a robust parsing function that handles all formats, NOT simple split operations
   - NEVER use operations that assume non-null values (like .split()) without first handling nulls and edge cases
   - Add a check: if converting strings to numeric, handle parsing errors with try-except or pd.to_numeric with errors='coerce'

IMPORTANT: If any column has null values, you MUST include explicit null-handling steps in cleaning_steps before any other operations.

For Duration columns, specify: "Convert Duration to minutes using a robust parsing function that handles 'Xh Ym', 'Ym', 'Xh', and empty values"

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
{profile_json}
```

### Prompt 2: The Coder (Stage 2 - Groq API)

```
You are an expert Python data analyst. Generate a COMPLETE, RUNNABLE Python script that performs the following analysis on a CSV file.

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
   - Create a mapping dictionary: mapping = {'value1': 1, 'value2': 2}
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
{data_profile}

ANALYSIS PLAN:
{analysis_plan}

Return ONLY the Python code, no markdown fences, no explanation.
```

### Prompt 3: The Narrator (Stage 4 - Gemini API)

```
You are a senior data analyst writing a report for stakeholders.

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
{analysis_results}
```

---

## 6. Results

The pipeline successfully:
- Processes any CSV dataset in under 60 seconds
- Generates professional visualizations automatically
- Produces coherent, stakeholder-ready narratives
- Creates self-contained HTML reports (no external dependencies)

**Time saved:** 2-4 hours per dataset to 45-60 seconds


