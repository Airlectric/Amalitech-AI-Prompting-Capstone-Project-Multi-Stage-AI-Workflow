import base64
import webbrowser
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

def image_to_base64(image_path):
    with open(image_path, "rb") as img:
        encoded = base64.b64encode(img.read()).decode("utf-8")
        return f"data:image/png;base64,{encoded}"

def build_report(narrative, chart_paths, profile):
    template_dir = Path(__file__).parent
    env = Environment(loader=FileSystemLoader(str(template_dir)))
    template = env.get_template("report_template.html")
    
    charts = []
    for i, chart_path in enumerate(chart_paths):
        charts.append({
            "title": f"Chart {i + 1}",
            "description": f"Analysis result {i + 1}",
            "data_uri": image_to_base64(chart_path)
        })
    
    context = {
        "filename": profile.get("filename", "Unknown"),
        "row_count": profile.get("row_count", 0),
        "column_count": profile.get("column_count", 0),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "executive_summary": narrative.get("executive_summary", "No summary available."),
        "key_findings": narrative.get("key_findings", []),
        "recommendations": narrative.get("recommendations", []),
        "charts": charts
    }
    
    html_content = template.render(context)
    
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    report_path = output_dir / "report.html"
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    webbrowser.open(f"file://{report_path.absolute()}")
    
    return str(report_path)

if __name__ == "__main__":
    import json
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python compiler.py <narrative_json> <chart_paths...>")
        sys.exit(1)
    
    narrative = json.loads(sys.argv[1])
    chart_paths = sys.argv[2:]
    
    profile = {
        "filename": "employees.csv",
        "row_count": 1000,
        "column_count": 12
    }
    
    report_path = build_report(narrative, chart_paths, profile)
    print(f"Report generated: {report_path}")
