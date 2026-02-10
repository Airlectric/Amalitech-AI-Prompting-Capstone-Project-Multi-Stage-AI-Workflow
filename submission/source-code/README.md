# Automated Intelligent Data Analysis Pipeline

## Overview

A single-command Python pipeline that automatically analyzes any CSV dataset and generates a complete, professional HTML report with charts, insights, and recommendations in under 60 seconds.

**Problem Solved:** Manual data analysis takes 2-4 hours per dataset. This pipeline reduces it to ~45 seconds with zero human intervention after initial CSV selection.

## Features

- **Fully Automated**: One command processes everything from raw CSV to final HTML report
- **AI-Powered**: Chains two different AI APIs (Gemini + Groq) for optimal results
- **Professional Reports**: Generates self-contained HTML reports with embedded charts
- **Multiple Visualizations**: Automatically creates appropriate charts for each analysis
- **Executive Summary**: AI-generated narrative with key findings and recommendations
- **Error Handling**: Saves partial results at each stage for debugging
- **Rate Limiting**: Built-in delays between API calls to avoid rate limits

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Copy environment template
cp .env.example .env

# 3. Add your API keys to .env
#    - GEMINI_API_KEY from https://aistudio.google.com
#    - GROQ_API_KEY from https://console.groq.com

# 4. Run the pipeline
python pipeline.py sample_data/employees.csv

# 5. Report opens automatically at output/report.html
```

## Project Structure

```
project/
├── pipeline.py              # Main orchestrator (6-stage pipeline)
├── profiler.py              # Stage 0: Data profiling
├── gemini_client.py         # Stage 1 & 4: Gemini API integration
├── groq_client.py           # Stage 2: Groq API integration
├── executor.py              # Stage 3: Code execution
├── compiler.py              # Stage 5: HTML report compilation
├── report_template.html     # Professional Jinja2 HTML template
├── generate_sample_data.py  # Synthetic employee data generator
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── sample_data/            # Sample datasets
│   └── employees.csv       # 1000 employee records
├── output/                 # Generated output files
│   ├── charts/             # PNG visualization files
│   └── report.html         # Final HTML report
└── docs/                   # Documentation
    ├── workflow-diagram.md  # Pipeline architecture diagram
    └── documentation.md     # Full documentation
```

## Pipeline Architecture

### Stage 0: Data Profiling (Python)
- Reads CSV file with pandas
- Extracts schema, statistics, sample rows
- Identifies column types (numeric, categorical, datetime)
- **Output**: JSON data profile

### Stage 1: AI Analysis Planning (Gemini API)
- Receives data profile
- Identifies dataset domain and purpose
- Generates 4-5 analytical questions
- Specifies chart types and analysis methods
- **Output**: JSON analysis plan

### Stage 2: AI Code Generation (Groq API)
- Receives data schema and analysis plan
- Generates complete, runnable Python script
- Creates visualizations using pandas/matplotlib/seaborn
- **Output**: Python analysis script

### Stage 3: Code Execution (Python)
- Executes generated script via subprocess
- 60-second timeout protection
- Captures stdout and collects PNG charts
- **Output**: Charts + JSON results

### Stage 4: AI Report Narration (Gemini API)
- Receives analysis results and chart descriptions
- Writes executive summary
- Generates key findings and recommendations
- **Output**: JSON narrative

### Stage 5: Report Compilation (Python)
- Loads Jinja2 HTML template
- Embeds charts as base64 images
- Injects narrative and metadata
- **Output**: Self-contained HTML report

## Tools Used

| Tool | Provider | Role | Model |
|------|----------|------|-------|
| Gemini API | Google | Analysis planning & narration | gemini-2.5-flash |
| Groq API | Groq | Python code generation | llama-3.3-70b-versatile |
| Pandas | - | Data processing | - |
| Matplotlib | - | Visualization | - |
| Seaborn | - | Statistical graphics | - |
| Jinja2 | - | HTML templating | - |
| Google GenAI SDK | Google | API client | - |
| Groq SDK | Groq | API client | - |

## API Keys Required

### Gemini API Key (Free Tier)
1. Go to [Google AI Studio](https://aistudio.google.com)
2. Sign in with Google account
3. Click "Get API Key"
4. Copy key to `.env` as `GEMINI_API_KEY`

### Groq API Key (Free Tier)
1. Go to [Groq Console](https://console.groq.com)
2. Sign up with GitHub/Google
3. Click "Create API Key"
4. Copy key to `.env` as `GROQ_API_KEY`

## Sample Data

The project includes a synthetic employee dataset with 1000 records:

| Column | Type | Description |
|--------|------|-------------|
| employee_id | categorical | Unique EMP##### format |
| name | categorical | Employee full name |
| age | numeric | 22-60 years |
| gender | categorical | Male/Female/Non-binary |
| department | categorical | Sales/Engineering/HR/Marketing/Finance |
| job_role | categorical | Role specific to department |
| salary | numeric | Role-based with variation |
| years_at_company | numeric | 0-25 years |
| satisfaction_score | numeric | 1.0-5.0 scale |
| overtime_hours | numeric | 0-40 hours/week |
| performance_rating | numeric | 1-5 scale |
| attrition | categorical | Yes/No |

## Error Handling

The pipeline saves partial results at each stage for debugging:

```
output/
├── stage0_profile.json        # Data profile
├── stage1_analysis_plan.json  # Analysis plan
├── stage2_analysis_script.py # Generated code
├── stage3_results.json        # Execution results
├── stage3_error.json         # Error details (if failed)
├── stage4_narrative.json     # Final narrative
├── charts/                   # Generated visualizations
└── report.html              # Final report
```

## Documentation

- **[Workflow Diagram](docs/workflow-diagram.md)**: Visual flowchart of the 6-stage pipeline
- **[Full Documentation](docs/documentation.md)**: Detailed explanation of all stages, prompts, and architecture

## Requirements

```
pandas>=1.5.0
matplotlib>=3.7.0
seaborn>=0.12.0
google-genai>=1.0.0
groq>=0.4.0
jinja2>=3.1.0
python-dotenv>=1.0.0
```

## License

MIT License

## Performance

| Metric | Before | After |
|--------|--------|-------|
| Analysis Time | 2-4 hours | ~45 seconds |
| Human Effort | Full engagement | Single command |
| Report Quality | Varies by analyst | Consistent, professional |
| Visualizations | Manual selection | Auto-generated |

## Troubleshooting

### Rate Limit Errors
- The pipeline includes 2-second delays between API calls
- If rate limits persist, wait 1-2 minutes and retry
- gemini-2.5-flash has higher free tier limits

### Module Not Found Errors
```bash
pip install -r requirements.txt
```

### Execution Timeout
- Default timeout is 60 seconds per stage
- Modify in `executor.py` if needed

### Empty Charts
- Check `output/stage3_error.json` for execution errors
- Verify CSV file has valid data
