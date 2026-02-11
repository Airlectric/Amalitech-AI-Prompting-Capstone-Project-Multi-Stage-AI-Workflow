import streamlit as st
import pandas as pd
import os
import sys
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import base64

st.set_page_config(
    page_title="AI Data Analysis Pipeline",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

SUPPORTED_FORMATS = {
    ".csv": "CSV (Comma Separated Values)",
    ".xlsx": "Excel (Microsoft Excel)",
    ".parquet": "Parquet (Apache Parquet)",
    ".json": "JSON (JavaScript Object Notation)",
    ".html": "HTML (HyperText Markup Language)"
}

def validate_csv(file_path):
    """Validate CSV file integrity."""
    errors = []
    try:
        df = pd.read_csv(file_path, nrows=100)
        if df.empty:
            errors.append("CSV file is empty")
        if len(df.columns) == 0:
            errors.append("CSV file has no columns")
        return {
            "valid": len(errors) == 0,
            "rows": len(df),
            "columns": list(df.columns),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "errors": errors
        }
    except Exception as e:
        return {
            "valid": False,
            "rows": 0,
            "columns": [],
            "dtypes": {},
            "errors": [f"Failed to parse CSV: {str(e)}"]
        }

def validate_xlsx(file_path):
    """Validate Excel file integrity."""
    errors = []
    try:
        xl = pd.ExcelFile(file_path)
        if len(xl.sheet_names) == 0:
            errors.append("Excel file has no sheets")
            return {
                "valid": False,
                "sheets": [],
                "rows": 0,
                "columns": [],
                "errors": errors
            }
        
        sheet_name = xl.sheet_names[0]
        df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=100)
        
        if df.empty:
            errors.append(f"Sheet '{sheet_name}' is empty")
        
        return {
            "valid": len(errors) == 0,
            "sheets": xl.sheet_names,
            "rows": len(df),
            "columns": list(df.columns),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "errors": errors
        }
    except Exception as e:
        return {
            "valid": False,
            "sheets": [],
            "rows": 0,
            "columns": [],
            "dtypes": {},
            "errors": [f"Failed to parse Excel file: {str(e)}"]
        }

def validate_parquet(file_path):
    """Validate Parquet file integrity."""
    errors = []
    try:
        df = pd.read_parquet(file_path)
        if df.empty:
            errors.append("Parquet file is empty")
        if len(df.columns) == 0:
            errors.append("Parquet file has no columns")
        return {
            "valid": len(errors) == 0,
            "rows": len(df),
            "columns": list(df.columns),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "errors": errors
        }
    except Exception as e:
        return {
            "valid": False,
            "rows": 0,
            "columns": [],
            "dtypes": {},
            "errors": [f"Failed to parse Parquet file: {str(e)}"]
        }

def validate_json(file_path):
    """Validate JSON file integrity."""
    errors = []
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        if isinstance(data, list):
            df = pd.DataFrame(data[:100])
        elif isinstance(data, dict):
            df = pd.DataFrame.from_dict(data, orient='index').T.head(100)
        else:
            errors.append("JSON format not recognized as valid data structure")
            return {
                "valid": False,
                "rows": 0,
                "columns": [],
                "dtypes": {},
                "errors": errors
            }
        
        if df.empty:
            errors.append("JSON file contains no valid data records")
        
        return {
            "valid": len(errors) == 0,
            "rows": len(df),
            "columns": list(df.columns),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "errors": errors
        }
    except Exception as e:
        return {
            "valid": False,
            "rows": 0,
            "columns": [],
            "dtypes": {},
            "errors": [f"Failed to parse JSON file: {str(e)}"]
        }

def validate_dataset(file_path, file_ext):
    """Validate dataset based on file extension."""
    validators = {
        ".csv": validate_csv,
        ".xlsx": validate_xlsx,
        ".parquet": validate_parquet,
        ".json": validate_json
    }
    
    validator = validators.get(file_ext.lower())
    if validator:
        return validator(file_path)
    else:
        return {
            "valid": True,
            "message": f"File extension {file_ext} accepted without validation"
        }

def convert_to_csv(input_path, output_path):
    """Convert any supported format to CSV."""
    ext = Path(input_path).suffix.lower()
    
    if ext == ".csv":
        shutil.copy(input_path, output_path)
    elif ext == ".xlsx":
        df = pd.read_excel(input_path)
        df.to_csv(output_path, index=False)
    elif ext == ".parquet":
        df = pd.read_parquet(input_path)
        df.to_csv(output_path, index=False)
    elif ext == ".json":
        with open(input_path, 'r') as f:
            data = json.load(f)
        if isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            df = pd.DataFrame.from_dict(data, orient='index')
        df.to_csv(output_path, index=False)
    else:
        raise ValueError(f"Unsupported format: {ext}")

def html_to_pdf(html_content, output_path):
    """Convert HTML report to PDF using WeasyPrint or pdfkit."""
    try:
        from weasyprint import HTML
        html_doc = HTML(string=html_content)
        html_doc.write_pdf(output_path)
        return True
    except ImportError:
        pass
    
    try:
        import pdfkit
        pdfkit.from_string(html_content, output_path, options={'encoding': 'UTF-8'})
        return True
    except ImportError:
        pass
    
    return False

def html_to_markdown(html_content, output_path):
    """Convert HTML report to Markdown."""
    try:
        from html2text import HTML2Text
        h = HTML2Text()
        h.ignore_links = False
        markdown_text = h.handle(html_content)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_text)
        return True
    except ImportError:
        pass
    
    return False

def run_pipeline(csv_path, progress_bar, status_text):
    """Run the analysis pipeline and return results."""
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from profiler import profile_csv
        from gemini_client import analyze_data, narrate_results
        from groq_client import generate_code
        from executor import run_analysis
        from compiler import build_report
        
        status_text.text("[Stage 0] Profiling dataset...")
        progress_bar.progress(10)
        data_profile = profile_csv(csv_path)
        status_text.text(f"  -> Found {data_profile['row_count']} rows, {data_profile['column_count']} columns")
        
        status_text.text("[Stage 1] AI analyzing data (Gemini)...")
        progress_bar.progress(25)
        import time
        time.sleep(1)
        analysis_plan = analyze_data(data_profile)
        status_text.text(f"  -> Generated {len(analysis_plan.get('analyses', []))} analysis questions")
        
        status_text.text("[Stage 2] AI generating analysis code (Groq/Llama)...")
        progress_bar.progress(40)
        time.sleep(1)
        code_string = generate_code(data_profile, analysis_plan)
        status_text.text(f"  -> Generated {len(code_string.splitlines())} lines of Python code")
        
        status_text.text("[Stage 3] Executing generated analysis...")
        progress_bar.progress(60)
        execution_result = run_analysis(code_string, csv_path)
        if not execution_result["success"]:
            return {"success": False, "error": execution_result.get("errors", "Unknown error")}
        status_text.text(f"  -> Execution successful, {len(execution_result['chart_paths'])} charts generated")
        
        status_text.text("[Stage 4] AI writing report narrative (Gemini)...")
        progress_bar.progress(80)
        time.sleep(1)
        narrative = narrate_results(execution_result.get("results", {}))
        status_text.text(f"  -> Generated executive summary and {len(narrative.get('key_findings', []))} key findings")
        
        status_text.text("[Stage 5] Compiling final report...")
        progress_bar.progress(90)
        report_path = build_report(narrative, execution_result["chart_paths"], data_profile)
        status_text.text(f"  -> Report saved to: {report_path}")
        
        progress_bar.progress(100)
        status_text.text("Pipeline completed successfully!")
        
        return {
            "success": True,
            "report_path": report_path,
            "data_profile": data_profile,
            "narrative": narrative,
            "chart_count": len(execution_result["chart_paths"])
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def main():
    st.title("📊 AI-Powered Data Analysis Pipeline")
    st.markdown("""
    Upload your dataset (CSV, Excel, Parquet, or JSON) and get a comprehensive 
    automated analysis with visualizations, insights, and recommendations.
    """)
    
    st.sidebar.header("Upload Dataset")
    uploaded_file = st.sidebar.file_uploader(
        "Choose a file",
        type=list(SUPPORTED_FORMATS.keys()),
        help=f"Supported formats: {', '.join(SUPPORTED_FORMATS.keys())}"
    )
    
    st.sidebar.header("API Configuration")
    st.sidebar.info("Configure your API keys in the .env file for full functionality.")
    
    if uploaded_file is not None:
        file_ext = Path(uploaded_file.name).suffix.lower()
        
        st.header("📁 Dataset Validation")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file_path = os.path.join(temp_dir, uploaded_file.name)
            
            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file.getvalue())
            
            with st.spinner("Validating dataset..."):
                validation_result = validate_dataset(temp_file_path, file_ext)
            
            if validation_result["valid"]:
                st.success("✅ Dataset validation passed!")
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Format", SUPPORTED_FORMATS.get(file_ext, file_ext))
                col2.metric("Rows", validation_result.get("rows", "N/A"))
                col3.metric("Columns", len(validation_result.get("columns", [])))
                
                with st.expander("View Dataset Preview"):
                    if file_ext in [".csv", ".parquet", ".json"]:
                        if file_ext == ".csv":
                            df = pd.read_csv(temp_file_path)
                        elif file_ext == ".parquet":
                            df = pd.read_parquet(temp_file_path)
                        else:
                            with open(temp_file_path, 'r') as f:
                                data = json.load(f)
                            df = pd.DataFrame(data) if isinstance(data, list) else pd.DataFrame.from_dict(data, orient='index')
                        st.dataframe(df.head(10), use_container_width=True)
                    elif file_ext == ".xlsx":
                        xl = pd.ExcelFile(temp_file_path)
                        sheet_name = xl.sheet_names[0]
                        df = pd.read_excel(temp_file_path, sheet_name=sheet_name)
                        st.dataframe(df.head(10), use_container_width=True)
                
                st.divider()
                
                if st.button("🚀 Run Analysis Pipeline", type="primary", use_container_width=True):
                    st.header("📈 Analysis Progress")
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    csv_path = os.path.join(temp_dir, "data.csv")
                    try:
                        convert_to_csv(temp_file_path, csv_path)
                        
                        with st.spinner("Running analysis pipeline... This may take a few minutes."):
                            result = run_pipeline(csv_path, progress_bar, status_text)
                        
                        if result["success"]:
                            st.success("🎉 Analysis completed successfully!")
                            
                            st.header("📋 Analysis Report")
                            
                            report_path = result["report_path"]
                            with open(report_path, 'r', encoding='utf-8') as f:
                                report_html = f.read()
                            
                            st.subheader("Report Preview")
                            with st.container(height=500):
                                st.components.v1.html(report_html, height=500, scrolling=True)
                            
                            st.divider()
                            
                            st.subheader("📥 Download Report")
                            download_format = st.radio(
                                "Select download format:",
                                ["HTML", "PDF", "Markdown"],
                                horizontal=True
                            )
                            
                            col1, col2 = st.columns(2)
                            
                            if download_format == "HTML":
                                st.download_button(
                                    label="📄 Download HTML Report",
                                    data=report_html,
                                    file_name=f"data_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                                    mime="text/html",
                                    use_container_width=True
                                )
                            
                            elif download_format == "PDF":
                                pdf_path = report_path.replace(".html", ".pdf")
                                if html_to_pdf(report_html, pdf_path):
                                    with open(pdf_path, 'rb') as f:
                                        pdf_data = f.read()
                                    st.download_button(
                                        label="📑 Download PDF Report",
                                        data=pdf_data,
                                        file_name=f"data_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                                        mime="application/pdf",
                                        use_container_width=True
                                    )
                                else:
                                    st.error("PDF conversion requires weasyprint or pdfkit. Install with: pip install weasyprint")
                                    st.info("Falling back to HTML download. You can convert HTML to PDF using browser print.")
                                    st.download_button(
                                        label="📄 Download HTML Report (print to PDF)",
                                        data=report_html,
                                        file_name=f"data_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                                        mime="text/html",
                                        use_container_width=True
                                    )
                            
                            elif download_format == "Markdown":
                                md_path = report_path.replace(".html", ".md")
                                if html_to_markdown(report_html, md_path):
                                    with open(md_path, 'r', encoding='utf-8') as f:
                                        md_data = f.read()
                                    st.download_button(
                                        label="📝 Download Markdown Report",
                                        data=md_data,
                                        file_name=f"data_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                                        mime="text/markdown",
                                        use_container_width=True
                                    )
                                else:
                                    st.error("Markdown conversion failed")
                            
                            st.divider()
                            
                            st.subheader("📊 Analysis Summary")
                            summary_cols = st.columns(3)
                            summary_cols[0].info(f"**Dataset:** {result['data_profile']['filename']}")
                            summary_cols[1].info(f"**Rows:** {result['data_profile']['row_count']}")
                            summary_cols[2].info(f"**Charts:** {result['chart_count']}")
                            
                            st.markdown("**Executive Summary:**")
                            st.markdown(f"_{result['narrative'].get('executive_summary', 'No summary available')}_")
                            
                            with st.expander("View Key Findings"):
                                for i, finding in enumerate(result['narrative'].get('key_findings', []), 1):
                                    st.markdown(f"{i}. {finding}")
                            
                            with st.expander("View Recommendations"):
                                for i, rec in enumerate(result['narrative'].get('recommendations', []), 1):
                                    st.markdown(f"{i}. {rec}")
                        
                        else:
                            st.error(f"Analysis failed: {result['error']}")
                            with st.expander("View Error Details"):
                                st.code(result.get("error", "Unknown error"))
                    
                    except Exception as e:
                        st.error(f"Pipeline execution error: {str(e)}")
                        with st.expander("View Traceback"):
                            st.code(exception_details=True)
            
            else:
                st.error("❌ Dataset validation failed!")
                for error in validation_result.get("errors", []):
                    st.error(f"  - {error}")
                
                if "columns" in validation_result and validation_result["columns"]:
                    st.warning("Detected columns:")
                    st.write(validation_result["columns"])
    
    else:
        st.info("👈 Upload a dataset from the sidebar to begin analysis")
        
        st.header("Supported Formats")
        format_cols = st.columns(len(SUPPORTED_FORMATS))
        for i, (ext, desc) in enumerate(SUPPORTED_FORMATS.items()):
            format_cols[i % 4].info(f"**{ext}**\n{desc}")
        
        st.header("How It Works")
        st.markdown("""
        1. **Upload** your dataset (CSV, Excel, Parquet, or JSON)
        2. **Validate** the file format and structure
        3. **Run** the AI-powered analysis pipeline
        4. **View** comprehensive report with visualizations
        5. **Download** in HTML, PDF, or Markdown format
        """)
        
        st.header("Features")
        st.markdown("""
        - 🤖 **AI-Powered Analysis** - Uses Gemini and Groq APIs for intelligent analysis
        - 📊 **Automated Visualizations** - Generates appropriate charts for your data
        - 📋 **Executive Summary** - AI-generated narrative with key findings
        - 💡 **Recommendations** - Actionable insights based on your data
        - 🔒 **Local Processing** - Your data stays on your machine
        """)

if __name__ == "__main__":
    main()
