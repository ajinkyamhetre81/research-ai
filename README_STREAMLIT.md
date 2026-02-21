# Research AI - Streamlit UI

A user-friendly web interface for the Research AI document analysis system, built with Streamlit. This UI provides an easy way to upload and process PDF documents using the existing FastAPI backend.

## Features

- 📁 **PDF File Upload**: Direct file upload with drag-and-drop support
- 🔗 **URL Processing**: Process PDFs directly from web URLs
- 📊 **Real-time Statistics**: View extraction metrics and processing information
- 📝 **Text Preview**: Browse extracted text page by page
- 💾 **Download Results**: Export extracted text as downloadable files
- ⚙️ **Configurable Options**: Customize page ranges and OCR languages
- 🎨 **Modern UI**: Clean, responsive interface with error handling

## Prerequisites

- Python 3.8+
- FastAPI backend server running
- All dependencies installed (see requirements.txt)

## Installation

1. **Clone/Download the project** (if not already done)

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the FastAPI backend**:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
   
   The backend API will be available at `http://localhost:8000`

4. **Run the Streamlit UI**:
   ```bash
   streamlit run streamlit_app.py
   ```

   The UI will open automatically in your browser at `http://localhost:8501`

## Usage

### 1. File Upload Method

1. Click on the **"📁 File Upload"** tab
2. Upload a PDF file using the file uploader
3. Configure optional settings in the sidebar:
   - **Page Range**: Specify pages to process (e.g., "1-5", "1,3,5")
   - **Languages**: Select OCR languages if needed
4. Click **"🚀 Process PDF"** to start processing
5. View results in the dashboard

### 2. URL Processing Method

1. Click on the **"🔗 URL Processing"** tab
2. Enter the URL of a PDF file
3. Configure optional settings in the sidebar
4. Click **"🌐 Process from URL"** to start processing
5. View results in the dashboard

### 3. Understanding the Results

- **File Information**: Shows filename, size, type, and extension
- **Extraction Statistics**: Displays total pages, word counts, and processing time
- **Extracted Text**: Browse text page by page with download options
- **Error Handling**: Clear error messages with suggestions for troubleshooting

## Configuration

### Sidebar Options

- **API Base URL**: Change if your backend runs on a different port/host
- **Page Range**: Limit processing to specific pages
  - Examples: "1-5" (pages 1-5), "1,3,5" (specific pages), "10-" (page 10 onwards)
- **Languages**: Select languages for OCR recognition
  - Default: English (eng)
  - Available: Spanish, French, German, Italian, Portuguese, Chinese, Japanese, Korean

### Supported File Formats

- **PDF**: Primary format with full text extraction support
- **File Size Limit**: 50MB (configurable in backend)

## API Integration

The Streamlit UI integrates with two main FastAPI endpoints:

1. **POST /api/v1/upload-pdf**: Process uploaded PDF files
2. **POST /api/v1/process-pdf-url**: Process PDFs from URLs

## Troubleshooting

### Common Issues

1. **Connection Error**:
   - Ensure the FastAPI backend is running on the correct port
   - Check the API Base URL in the sidebar configuration

2. **File Upload Fails**:
   - Verify the file is a valid PDF
   - Check file size (max 50MB)
   - Ensure the file isn't corrupted

3. **URL Processing Fails**:
   - Verify the URL is accessible
   - Ensure the URL points to a valid PDF file
   - Check for authentication requirements

4. **No Text Extracted**:
   - The PDF might be image-based (scanned)
   - Try enabling OCR languages in the sidebar
   - Check if the PDF contains selectable text

### Error Messages

The UI provides detailed error messages with:
- **Error Codes**: Specific error identifiers
- **Descriptions**: Human-readable explanations
- **Suggestions**: Recommended actions to resolve issues
- **Technical Details**: Additional debugging information (expandable)

## Development

### Customizing the UI

The main UI file is `streamlit_app.py`. Key sections:

- **Layout**: Page configuration and CSS styling
- **Sidebar**: Configuration options and inputs
- **Tabs**: File upload and URL processing interfaces
- **API Integration**: Functions to communicate with FastAPI backend
- **Result Display**: Functions to show processing results

### Adding New Features

1. Add new UI elements in the appropriate tab
2. Create corresponding API integration functions
3. Update the result display functions as needed
4. Test with the FastAPI backend

## Performance Tips

- **Large Files**: Processing large PDFs may take time; be patient
- **Network URLs**: URL processing depends on internet speed and file size
- **Page Ranges**: Use page ranges to process only needed pages for faster results
- **OCR**: OCR processing is slower than direct text extraction

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Verify the FastAPI backend is running correctly
3. Check the browser console for JavaScript errors
4. Review the backend logs for API-related issues

---

**Research AI** - Document Analysis Tool  
Powered by FastAPI & Streamlit
