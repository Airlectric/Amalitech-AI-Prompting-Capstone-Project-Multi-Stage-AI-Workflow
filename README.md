# Automated Intelligent Data Analysis Pipeline

## Overview

A single-command Python pipeline that automatically analyzes any CSV dataset and generates a complete HTML report with charts, insights, and recommendations.

## Installation

```bash
pip install -r requirements.txt
```

## Setup

1. Copy `.env.example` to `.env`
2. Add your API keys:
   - Gemini API Key from [Google AI Studio](https://aistudio.google.com)
   - Groq API Key from [Groq Console](https://console.groq.com)

## Usage

```bash
python pipeline.py sample_data/employees.csv
```

The report will be generated at `output/report.html` and opened automatically in your browser.

## Project Structure

```
project/
├── pipeline.py           # Main orchestrator
├── profiler.py           # Stage 0: data profiling
├── gemini_client.py      # Stage 1 & 4: Gemini API calls
├── groq_client.py        # Stage 2: Groq API calls
├── executor.py            # Stage 3: runs generated code
├── compiler.py            # Stage 5: builds HTML report
├── report_template.html   # Jinja2 HTML template
├── requirements.txt      # Python dependencies
├── .env.example          # API keys template
├── sample_data/          # Test CSV files
│   └── employees.csv
└── output/               # Generated reports
    ├── charts/
    └── report.html
```

## Pipeline Stages

1. **Profiler** - Extracts schema and statistics from CSV
2. **Gemini (Analyst)** - Creates analysis plan
3. **Groq (Coder)** - Generates Python analysis script
4. **Executor** - Runs the script, produces charts
5. **Gemini (Narrator)** - Writes executive summary
6. **Compiler** - Assembles final HTML report

## Tools Used

- **Gemini API** - Data analysis planning and report narration
- **Groq API (Llama 3.3)** - Python code generation
- **Pandas/Matplotlib/Seaborn** - Data processing and visualization
