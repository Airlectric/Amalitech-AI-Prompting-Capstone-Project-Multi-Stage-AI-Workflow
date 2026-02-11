# Prompt Logs

This document records user prompts given to the AI to accomplish all project tasks.

---

## Project Setup Prompts

### Prompt 1: Initial Project Setup
Create a Python project for an Automated Intelligent Data Analysis Pipeline with the following structure:
- pipeline.py - Main orchestrator
- profiler.py - Data profiling module
- gemini_client.py - Gemini API integration
- groq_client.py - Groq API integration
- executor.py - Code execution module
- compiler.py - HTML report compiler
- report_template.html - Jinja2 HTML template
- requirements.txt with: pandas, matplotlib, seaborn, google-genai, groq, jinja2, python-dotenv
- sample_data/ directory with .gitkeep
- output/ directory with charts/ subdirectory
- .env.example with GEMINI_API_KEY and GROQ_API_KEY

---

## Data Profiling Enhancement Prompts

### Prompt 2: Enhanced Numeric Statistics
Enhance profiler.py to include comprehensive statistics for numeric columns:
- count, null_count, null_percentage
- mean, median, mode
- min, max, range
- variance, std, coefficient_of_variation
- skewness, kurtosis
- percentile_25, percentile_50 (median), percentile_75
- IQR (Interquartile Range)

### Prompt 3: Enhanced Categorical Statistics
Enhance profiler.py to include comprehensive statistics for categorical columns:
- count, null_count, null_percentage
- unique_count, unique_values
- value_counts with top 10 values
- mode (most common value)
- mode_frequency, mode_percentage

### Prompt 4: Add Total Null Count
Update profiler.py to include total_null_values at the dataset level (sum of all null values across all columns).

---

## Report Template Enhancement Prompts

### Prompt 5: Data Profile Section
Update report_template.html to add a new "Data Profile" section before the Executive Summary that displays:
- Dataset overview: Total Rows, Total Columns, Total Null Values
- For each column, display statistics in organized categories:
  - Central Tendency: count, mean, median, mode
  - Dispersion: min, max, range, variance, std, coefficient of variation
  - Shape: skewness, kurtosis
  - Percentiles: Q1, Median, Q3, IQR
- Use styled tables with alternating row colors
- Add visual distribution bars for categorical columns
- Add null warnings when columns contain missing data

### Prompt 6: Update Compiler for Enhanced Data
Update compiler.py to pass total_null_values and columns data to the report template context.

---

## Null Handling Improvement Prompts

### Prompt 7: Improve Gemini Analysis Prompt
Update gemini_client.py's analyze_data function to include instructions for handling:
- Specific null value handling for each column with nulls
- Edge cases in string parsing (like "non-stop" or empty strings)
- Proper fillna syntax for modern pandas versions
- Parsing error handling with try-except or pd.to_numeric with errors='coerce'

### Prompt 8: Improve Groq Code Generation Prompt
Update groq_client.py's generate_code function to include:
- Correct pandas fillna syntax: df.loc[:, 'column_name'] = df['column_name'].fillna(value)
- For converting categorical to numeric: use mapping dict + pd.to_numeric + fillna + astype(int)
- For datetime conversion: df['column'] = pd.to_datetime(df['column'], format='mixed', dayfirst=True)
- UTF-8 file encoding for handling unicode characters

### Prompt 9: Fix File Encoding Issues
Update pipeline.py and executor.py to use encoding="utf-8" when writing files to handle unicode characters like arrows (→) in the generated code.

### Prompt 10: Increase Execution Timeout
Update executor.py to increase subprocess timeout from 60 seconds to 120 seconds for datasets with many rows.

---

## Testing and Integration Prompts

### Prompt 12: Test on Employees Dataset
Run the pipeline with sample_data/employees.csv and verify:
- Enhanced statistics are displayed correctly
- All 6 stages complete successfully
- Report generates with comprehensive data profile section

### Prompt 13: Test on Flight Dataset
Run the pipeline with sample_data/Flight_Price_Dataset_of_Bangladesh.csv and verify:
- Null values are properly detected and handled
- AI-generated code executes without errors
- Report generates successfully with 64 charts

---

### Prompt 14: Create Streamlit Frontend
Create a Streamlit frontend (app.py) with:
- File upload for .csv, .xlsx, .parquet, .json formats
- Dataset validation for all supported formats
- Pipeline integration with progress display
- HTML report display in embedded viewer
- Download options for HTML, PDF, and Markdown formats
- Update requirements.txt with new dependencies

---

### Prompt 15: Add Enhanced Streamlit Features
Enhance the Streamlit app with:
1. **Auto Cleanup**: Clear generated files after 30 minutes of inactivity using a background thread
2. **Sample Datasets**: Add sidebar option to test with existing datasets (employees.csv, Flight_Price_Dataset_of_Bangladesh.csv)
3. **Complete Package Download**: Add option to download report + all visualizations as a ZIP file containing:
   - HTML report
   - All generated PNG charts in a charts/ subfolder
4. **Manual Cleanup Button**: Add "Done - Clear Generated Files" button after analysis completion

Implementation details:
- Use threading.Timer or background thread for 30-min cleanup
- Create SESSION_DIR for session-based file management
- Implement create_zip_package() function using zipfile module
- Add cleanup_current_session() function for manual cleanup
- Create two tabs in download section: "Report Only" and "Complete Package"
- Add get_sample_datasets() function to discover available sample data

---

### Prompt 16: Update Prompt Logs
Update docs/prompt-logs.md to include all new prompts for enhanced Streamlit features.

---

### Prompt 17: Handle Gemini API Rate Limiting
The Gemini API free tier has a limit of 20 requests per minute. Implement fixes:

1. **Add Rate Limiting**: 
   - Add global LAST_API_CALL_TIME tracker
   - Implement rate_limit() function with 3-second cooldown between API calls
   - Use time.sleep() to enforce minimum delay between requests

2. **Add Retry Logic with Exponential Backoff**:
   - Create max_retries parameter (default 3 retries)
   - Implement fallback to different models when quota exceeded:
     - Primary: gemini-2.5-flash
     - Fallback 1: gemini-1.5-flash
     - Fallback 2: gemini-1.5-pro
   - Extract wait time from error message (e.g., "retry in 56.6s")
   - Add 5-second buffer to recommended wait time
   - Try each model sequentially before retrying

3. **Update Function Signatures**:
   - analyze_data(profile_json, max_retries=3)
   - narrate_results(analysis_results, max_retries=3)

4. **Error Handling**:
   - Catch RESOURCE_EXHAUSTED (429) errors
   - Parse error message for retry delay
   - Raise ValueError with clear message after all retries exhausted
   - Continue to next model if one fails due to quota





