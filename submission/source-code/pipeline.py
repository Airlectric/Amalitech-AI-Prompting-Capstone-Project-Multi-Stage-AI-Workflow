import sys
import json
import time
import traceback
from pathlib import Path
from dotenv import load_dotenv

from profiler import profile_csv
from gemini_client import analyze_data, narrate_results
from groq_client import generate_code
from executor import run_analysis
from compiler import build_report

load_dotenv()

def print_stage(stage_num, description):
    print(f"[Stage {stage_num}] {description}")

def save_partial_results(stage_name, data, filename):
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    filepath = output_dir / filename
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)
    print(f"  -> Saved partial results to {filepath}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python pipeline.py <csv_file>")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    
    if not Path(csv_path).exists():
        print(f"Error: File not found: {csv_path}")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("  Automated Intelligent Data Analysis Pipeline")
    print("="*60 + "\n")
    
    data_profile = None
    analysis_plan = None
    code_string = None
    execution_result = None
    narrative = None
    
    try:
        print_stage(0, "Profiling dataset...")
        data_profile = profile_csv(csv_path)
        print(f"  -> Found {data_profile['row_count']} rows, {data_profile['column_count']} columns\n")
        save_partial_results(0, data_profile, "stage0_profile.json")
        
        time.sleep(2)
        print_stage(1, "AI analyzing data (Gemini)...")
        analysis_plan = analyze_data(data_profile)
        print(f"  -> Generated {len(analysis_plan.get('analyses', []))} analysis questions\n")
        save_partial_results(1, analysis_plan, "stage1_analysis_plan.json")
        
        time.sleep(2)
        print_stage(2, "AI generating analysis code (Groq/Llama)...")
        code_string = generate_code(data_profile, analysis_plan)
        print(f"  -> Generated {len(code_string.splitlines())} lines of Python code\n")
        with open("output/stage2_analysis_script.py", "w") as f:
            f.write(code_string)
        
        time.sleep(2)
        print_stage(3, "Executing generated analysis...")
        execution_result = run_analysis(code_string, csv_path)
        if execution_result["success"]:
            print(f"  -> Execution successful, {len(execution_result['chart_paths'])} charts generated\n")
            save_partial_results(3, execution_result.get("results", {}), "stage3_results.json")
        else:
            print(f"  -> Execution failed: {execution_result.get('errors', 'Unknown error')}\n")
            save_partial_results(3, {"error": execution_result.get('errors')}, "stage3_error.json")
            sys.exit(1)
        
        time.sleep(2)
        print_stage(4, "AI writing report narrative (Gemini)...")
        narrative = narrate_results(execution_result.get("results", {}))
        print(f"  -> Generated executive summary and {len(narrative.get('key_findings', []))} key findings\n")
        save_partial_results(4, narrative, "stage4_narrative.json")
        
        time.sleep(2)
        print_stage(5, "Compiling final report...")
        report_path = build_report(narrative, execution_result["chart_paths"], data_profile)
        print(f"  -> Report saved to: {report_path}\n")
        
        print("="*60)
        print("  Pipeline completed successfully!")
        print("="*60 + "\n")
    
    except KeyboardInterrupt:
        print("\n\nPipeline interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        print("\nPartial results saved for debugging:")
        print("-" * 40)
        traceback.print_exc()
        print("-" * 40)
        sys.exit(1)

if __name__ == "__main__":
    main()
