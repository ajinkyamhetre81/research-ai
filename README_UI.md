# Document Processing Hub

A unified interface for PDF processing and website scraping.

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r ui/requirements.txt
   ```

2. **Start backend:**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Start UI:**
   ```bash
   streamlit run ui/app.py
   ```

4. **Access:**
   - Backend API: http://localhost:8000
   - Frontend UI: http://localhost:8501

## Features

- **📄 PDF Processing**: Upload files or process from URLs
- **🕷️ Website Scraping**: JavaScript-enabled crawling
- **📊 Multiple Views**: Table, detailed, and export formats
- **📥 Export Options**: JSON, CSV, TXT, Markdown

## File Structure

```
ui/
├── app.py                    # Main unified application
├── run.py                   # Entry point script
├── requirements.txt          # UI dependencies
├── README.md               # This file
└── streamlit_app_original.py # Original app (backup)
```

For detailed documentation, see `ui/README.md`.
