# Automated Intelligent Data Analysis Pipeline

## What This Does

Give it a dataset, and it hands you back a full analysis report — charts, insights, and recommendations — without you writing a single line of analysis code. The whole process takes under 60 seconds.

It works in two ways:
- **Terminal**: Run one command and get your report.
- **Web App**: Upload your file through a browser interface (Streamlit) and view/download results interactively.

## How It Works

The system runs your data through a 6-step pipeline. Each step feeds into the next:

```
Your CSV file
     |
     v
[Step 0] Profile the data
         Scans a sample of your dataset (up to 2,000 rows) to understand
         its shape — column names, types, value ranges, missing data, etc.
         The full dataset is still used later for the actual analysis.
     |
     v
[Step 1] AI plans the analysis  (Gemini API)
         The data profile is sent to Google's Gemini model. It figures out
         what the dataset is about and picks 4-5 interesting questions to
         answer — for example "How does salary vary by department?" — along
         with the right chart type for each one.
     |
     v
[Step 2] AI writes the analysis code  (Groq API)
         A second AI (Llama model via Groq) receives the profile and the
         analysis plan, then generates a complete Python script that will
         crunch the numbers and draw the charts.
     |
     v
[Step 3] Run the generated code
         The system executes the AI-written script in an isolated process.
         It reads your full dataset, performs the analyses, and saves
         charts as PNG images. If one analysis fails, the rest still run.
     |
     v
[Step 4] AI writes the narrative  (Gemini API)
         The raw results go back to Gemini, which writes a plain-English
         executive summary, highlights key findings, and suggests next steps.
     |
     v
[Step 5] Build the final report
         Everything is assembled into a single self-contained HTML file —
         narrative text, embedded charts, and metadata — using a template.
         Open it in any browser, no server needed.
```

## Fallback APIs

If the primary API hits a rate limit or goes down, the system automatically tries a backup:

| Step | Primary API | Fallback |
|------|-------------|----------|
| Analysis planning (Step 1) | Gemini | OpenRouter (DeepSeek V3) |
| Code generation (Step 2) | Groq (Llama) | Cerebras (Llama) |
| Report narration (Step 4) | Gemini | OpenRouter (DeepSeek V3) |

You only need API keys for the services you want to use. At minimum, a Gemini key and a Groq key will get you running.

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set up API keys

```bash
cp .env.example .env
```

Open `.env` and add your keys:

| Key | Where to get it (free) |
|-----|------------------------|
| `GOOGLE_API_KEY` | [Google AI Studio](https://aistudio.google.com) |
| `GROQ_API_KEY` | [Groq Console](https://console.groq.com) |
| `CEREBRAS_API_KEY` *(optional)* | [Cerebras](https://cloud.cerebras.ai) |
| `OPENROUTER_API_KEY` *(optional)* | [OpenRouter](https://openrouter.ai) |

### 3. Run it

**Terminal mode:**

```bash
python pipeline.py sample_data/employees.csv
```

The report appears at `output/report.html` and opens in your browser.

**Web app mode:**

```bash
streamlit run app.py
```

Opens at `http://localhost:8501`. Upload a file or pick a sample dataset from the sidebar, then click "Run Analysis Pipeline".

## Supported File Formats

The web app accepts CSV, Excel (.xlsx), Parquet, and JSON. Non-CSV formats are automatically converted to CSV before processing.

## Project Structure

```
pipeline.py              Main CLI entry point — runs the 6-step pipeline
app.py                   Streamlit web interface
profiler.py              Step 0: Scans and profiles the dataset
gemini_client.py         Steps 1 & 4: Gemini API calls (+ OpenRouter fallback)
groq_client.py           Step 2: Groq API call (+ Cerebras fallback)
executor.py              Step 3: Runs the AI-generated script safely
compiler.py              Step 5: Assembles the HTML report
report_template.html     HTML/CSS template for the final report
requirements.txt         Python packages needed
.env.example             Template for API keys
sample_data/             Sample datasets to test with
output/                  Where reports, charts, and intermediate files land
docs/                    Additional documentation
```

## What Gets Sent to the AI

The AI never sees your raw data. The profiler creates a summary that includes:

- Column names, data types, and basic statistics (mean, median, min/max, etc.)
- 3 sample rows so the AI understands the format
- For large datasets (over 2,000 rows), statistics are computed on a random sample

The generated analysis code runs locally on your machine against the full dataset.

## Troubleshooting

**Rate limit errors** — The pipeline waits between API calls, but if you hit limits, wait a minute and retry. The fallback APIs will also kick in automatically.

**Module not found** — Run `pip install -r requirements.txt` (use the venv if you have one).

**Analysis script fails** — The AI-generated code isn't perfect every time. The system is built to handle this: if some analyses fail, the ones that succeeded still make it into the report. Re-running often produces different (working) code.

**Partial results** — Each step saves its output to `output/` (e.g. `stage0_profile.json`, `stage1_analysis_plan.json`), so you can inspect where things went wrong.

## Requirements

- Python 3.8+
- At minimum: a Gemini API key and a Groq API key (both free tier)

## License

MIT License
