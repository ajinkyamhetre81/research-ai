# Document Processing Hub

A comprehensive Streamlit application that combines PDF processing and website scraping functionalities in a single, unified interface.

## 📁 File Structure

```
ui/
├── app.py                 # Main unified application
└── requirements.txt       # UI dependencies
```

## 🚀 Getting Started

### 1. Install Dependencies

```bash
cd ui
pip install -r requirements.txt
```

### 2. Run the Application

```bash
# Method 1: Direct run
streamlit run ui/app.py

# Method 2: From the ui directory
cd ui
streamlit run app.py
```

### 3. Access the Application

Open your browser and navigate to:
- `http://localhost:8501` (default Streamlit port)

## 🎯 Features

### **📄 PDF Processing Tab**

#### **Upload Mode**
- **File Upload**: Drag & drop or browse PDF files
- **File Preview**: In-browser PDF preview
- **File Info**: Display file size, type, and name
- **Processing**: Extract text from uploaded PDFs
- **Results**: View extracted text by pages
- **Export**: Download as JSON, TXT, or CSV

#### **URL Mode**
- **URL Input**: Process PDFs from web URLs
- **URL Validation**: Check if URL points to valid PDF
- **Remote Processing**: Download and process PDF from URL
- **Error Handling**: Comprehensive error messages

#### **PDF Features**
- **Multi-page Support**: Process all pages in PDF
- **Text Extraction**: Clean text extraction with formatting
- **Character Count**: Track extraction statistics
- **Page Navigation**: Easy browsing between pages
- **Multiple Views**: Table, detailed, and download views

### **🕷️ Website Scraping Tab**

#### **Crawl Configuration**
- **URL Input**: Enter any website URL
- **Page Limits**: Control crawling scope (1-500 pages)
- **Depth Control**: Set link-following depth (1-10)
- **Concurrency**: Adjust concurrent requests
- **Display Options**: Toggle content visibility

#### **Crawling Features**
- **JavaScript Rendering**: Handle dynamic websites
- **Smart Content Extraction**: Filter out noise
- **Link Discovery**: Follow internal links automatically
- **Progress Tracking**: Real-time crawling progress
- **Error Handling**: Robust error recovery

#### **Results & Export**
- **Multiple Views**: Table, detailed, and export views
- **Export Formats**: JSON, CSV, Markdown
- **Performance Metrics**: Success rates and timing
- **Content Preview**: Quick previews of crawled pages

## 🔧 Configuration

### **API Connection**
The UI automatically connects to the backend API at `http://localhost:8000`. 
You can change this in the sidebar configuration.

### **Sidebar Options**
- **API URL**: Configure backend connection
- **PDF Options**: Page range, OCR languages
- **Website Options**: Max pages, depth, concurrency
- **Display Options**: Content visibility settings

## 📱 Usage Instructions

### **Prerequisites**
1. **Backend Server**: Ensure FastAPI server is running
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Dependencies**: Install all required packages
   ```bash
   pip install -r ui/requirements.txt
   ```

### **PDF Processing Workflow**
1. **Select Tab**: Click on "📄 PDF Processing" tab
2. **Choose Mode**: Select "Upload PDF File" or "Process PDF from URL"
3. **Upload/Enter**: Upload file or enter PDF URL
4. **Configure**: Set processing options in sidebar
5. **Process**: Click the process button
6. **View Results**: Browse extracted content
7. **Download**: Export in preferred format

### **Website Scraping Workflow**
1. **Select Tab**: Click on "🕷️ Website Scraping" tab
2. **Configure**: Set crawl parameters in sidebar
3. **Enter URL**: Provide website URL to crawl
4. **Start Crawling**: Click the crawl button
5. **Monitor**: Watch real-time progress
6. **Export**: Download results

## 🎨 UI Features

### **Navigation**
- **Tab-based Interface**: Easy switching between PDF and website tools
- **Responsive Design**: Works on desktop and mobile
- **Professional Layout**: Clean, modern interface
- **Intuitive Controls**: User-friendly controls and options

### **Data Display**
- **Table Views**: Sortable, filterable data tables
- **Detailed Views**: Expandable cards with full information
- **Progress Indicators**: Real-time processing status
- **Metrics Dashboard**: Key performance indicators

### **Export Options**
- **JSON**: Complete structured data
- **CSV**: Tabular format for analysis
- **TXT**: Plain text for PDF content
- **Markdown**: Formatted reports for web data

## 🛠️ Development

### **Architecture**
The unified UI is built with a class-based structure:

```python
class DocumentProcessingHub:
    def __init__(self):
        # Initialize the application
    
    def render_pdf_processing_tab(self, config):
        # PDF processing interface
    
    def render_website_scraping_tab(self, config):
        # Website scraping interface
    
    def run(self):
        # Main application loop
```

### **Adding New Features**
1. **New Tabs**: Add tabs in the main `run()` method
2. **New Components**: Create separate methods for new features
3. **API Integration**: Add API calls in dedicated methods
4. **Export Formats**: Extend download options

## 🐛 Troubleshooting

### **Common Issues**

1. **Connection Error**: 
   - Ensure FastAPI server is running on port 8000
   - Check network connectivity
   - Verify API endpoints are accessible

2. **PDF Processing Issues**:
   - Check file format (must be PDF)
   - Verify file size limits
   - Ensure proper file permissions

3. **Website Scraping Issues**:
   - Verify URL is accessible
   - Check if website blocks crawling
   - Reduce concurrency for problematic sites

4. **Import Errors**:
   - Install all requirements: `pip install -r ui/requirements.txt`
   - Check Python path configuration
   - Verify Streamlit installation

## 📝 Notes

### **Security Considerations**
- **File Upload**: Validates file types and sizes
- **URL Processing**: Validates and sanitizes URLs
- **Error Handling**: Prevents information leakage
- **Rate Limiting**: Built-in request delays

### **Best Practices**
- **User Feedback**: Clear progress indicators and messages
- **Error Recovery**: Graceful handling of failures
- **Data Validation**: Input validation and sanitization
- **Performance**: Efficient data handling and display

## 🔄 Integration with Backend

### **PDF Processing API**
```python
# Upload PDF
POST /upload-pdf
Content-Type: multipart/form-data

# Process PDF URL
POST /process-pdf-url
Content-Type: application/json
```

### **Website Scraping API**
```python
# Crawl Website
POST /crawl-website
Content-Type: application/json
```

### **Response Format**
All APIs return consistent JSON responses with:
- `success`: Boolean indicating operation success
- `data`: Processed results or error information
- `metadata`: Additional context and statistics

This unified interface provides a seamless experience for both PDF processing and website scraping, with consistent design patterns and comprehensive functionality.
