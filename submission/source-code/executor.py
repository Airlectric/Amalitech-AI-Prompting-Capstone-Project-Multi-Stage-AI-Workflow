import subprocess
import os
import sys
import json
import glob
from pathlib import Path

OUTPUT_DIR = Path("output")
CHARTS_DIR = OUTPUT_DIR / "charts"
ANALYSIS_SCRIPT = OUTPUT_DIR / "analysis_script.py"

def ensure_directories():
    OUTPUT_DIR.mkdir(exist_ok=True)
    CHARTS_DIR.mkdir(exist_ok=True)

def run_analysis(code_string, csv_path):
    ensure_directories()
    
    with open(ANALYSIS_SCRIPT, "w") as f:
        f.write(code_string)
    
    result = {
        "success": False,
        "results": None,
        "chart_paths": [],
        "errors": None
    }
    
    try:
        process = subprocess.run(
            [sys.executable, str(ANALYSIS_SCRIPT), csv_path],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(OUTPUT_DIR)
        )
        
        result["stdout"] = process.stdout
        result["stderr"] = process.stderr
        result["return_code"] = process.returncode
        
        if process.returncode == 0:
            result["success"] = True
            try:
                result["results"] = json.loads(process.stdout.strip())
            except json.JSONDecodeError:
                result["results"] = {"raw_output": process.stdout.strip()}
        else:
            result["errors"] = process.stderr.strip() or f"Exit code: {process.returncode}"
    
    except subprocess.TimeoutExpired:
        result["errors"] = "Execution timed out after 60 seconds"
    except Exception as e:
        result["errors"] = str(e)
    
    chart_paths = list(CHARTS_DIR.glob("*.png"))
    result["chart_paths"] = [str(p) for p in chart_paths]
    
    return result

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python executor.py <code_string> <csv_path>")
        sys.exit(1)
    
    code_string = sys.argv[1]
    csv_path = sys.argv[2]
    
    result = run_analysis(code_string, csv_path)
    print(json.dumps(result, indent=2))
