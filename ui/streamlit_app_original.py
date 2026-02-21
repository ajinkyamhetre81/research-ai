import streamlit as st
import requests
import io
from typing import Optional
import json
from datetime import datetime

# Configure page
st.set_page_config(
    page_title="Research AI - Document Analysis",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    .stat-card {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 0.5rem;
        padding: 1rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Backend API configuration
API_BASE_URL = "http://localhost:8000"

def main():
    st.markdown('<h1 class="main-header">📄 Research AI - Document Analysis</h1>', unsafe_allow_html=True)
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        api_url = st.text_input("API Base URL", value=API_BASE_URL, help="URL of the FastAPI backend")
        
        st.header("📊 Processing Options")
        page_range = st.text_input(
            "Page Range (optional)", 
            placeholder="e.g., 1-5, 8, 10-12",
            help="Specify pages to process (e.g., '1-5' for pages 1-5, '1,3,5' for specific pages)"
        )
        
        languages = st.multiselect(
            "Languages for OCR",
            options=['eng', 'spa', 'fra', 'deu', 'ita', 'por', 'chi_sim', 'jpn', 'kor'],
            default=['eng'],
            help="Select languages for text recognition (if OCR is needed)"
        )
    
    # Main content tabs
    tab1, tab2 = st.tabs(["📁 File Upload", "🔗 URL Processing"])
    
    with tab1:
        st.header("Upload PDF Document")
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type=['pdf'],
            help="Upload a PDF file for text extraction and analysis"
        )
        
        if uploaded_file is not None:
            st.info(f"File selected: {uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)")
            
            if st.button("🚀 Process PDF", type="primary"):
                process_uploaded_file(uploaded_file, api_url, page_range, languages)
    
    with tab2:
        st.header("Process PDF from URL")
        pdf_url = st.text_input(
            "PDF URL",
            placeholder="https://example.com/document.pdf",
            help="Enter the URL of a PDF file to process"
        )
        
        if pdf_url:
            st.info(f"URL provided: {pdf_url}")
            
            if st.button("🌐 Process from URL", type="primary"):
                process_pdf_url(pdf_url, api_url, page_range, languages)

def process_uploaded_file(uploaded_file, api_url, page_range, languages):
    """Process uploaded PDF file through the API"""
    
    with st.spinner("🔄 Processing PDF..."):
        try:
            # Prepare API endpoint
            endpoint = f"{api_url}/api/v1/upload-pdf"
            
            # Prepare files and data
            files = {'upload_file': (uploaded_file.name, uploaded_file.getvalue(), 'application/pdf')}
            data = {}
            if page_range:
                data['page_range'] = page_range
            
            # Make API call
            response = requests.post(endpoint, files=files, data=data, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                display_success_result(result, source="file")
            else:
                display_error(response)
                
        except requests.exceptions.RequestException as e:
            st.error(f"🔴 Connection Error: Unable to connect to the API server at {api_url}")
            st.error("Please ensure the FastAPI server is running and accessible.")
            st.code(f"Error details: {str(e)}")

def process_pdf_url(pdf_url, api_url, page_range, languages):
    """Process PDF from URL through the API"""
    
    with st.spinner("🔄 Processing PDF from URL..."):
        try:
            # Prepare API endpoint
            endpoint = f"{api_url}/api/v1/process-pdf-url"
            
            # Prepare request data
            request_data = {
                "pdf_url": pdf_url,
                "languages": languages
            }
            if page_range:
                request_data["page_range"] = page_range
            
            # Make API call
            response = requests.post(endpoint, json=request_data, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                display_success_result(result, source="url")
            else:
                display_error(response)
                
        except requests.exceptions.RequestException as e:
            st.error(f"🔴 Connection Error: Unable to connect to the API server at {api_url}")
            st.error("Please ensure the FastAPI server is running and accessible.")
            st.code(f"Error details: {str(e)}")

def display_success_result(result, source):
    """Display successful processing results in JSON format"""
    
    st.success("✅ PDF processed successfully!")
    
    # Display format selector
    display_format = st.radio("Display Format:", ["JSON", "Markdown"], horizontal=True)
    
    if display_format == "JSON":
        st.subheader("📊 API Response (JSON)")
        st.json(result)
    else:
        st.subheader("📊 API Response (Markdown)")
        
        # File information
        if 'file_info' in result:
            st.markdown("### 📋 File Information")
            file_info = result['file_info']
            st.markdown(f"""
            - **Filename:** {file_info['filename']}
            - **Size:** {file_info['file_size'] / 1024:.1f} KB
            - **Type:** {file_info['mime_type']}
            - **Extension:** {file_info['extension']}
            """)
        
        # Processing statistics
        if 'extraction_summary' in result:
            st.markdown("### 📊 Extraction Statistics")
            summary = result['extraction_summary']
            st.markdown(f"""
            - **Total Pages:** {summary['total_pages']}
            - **Pages with Content:** {summary['pages_with_content']}
            - **Total Words:** {summary['total_words_extracted']:,}
            - **Average Words/Page:** {summary['avg_words_per_page']:.1f}
            - **Extraction Method:** {summary['extraction_method']}
            - **Processing Time:** {result.get('processing_time_ms', 0):.1f} ms
            """)
        
        # Extracted text
        if 'pages_data' in result and result['pages_data']:
            st.markdown("### 📝 Extracted Text")
            
            pages = result['pages_data']
            
            for page_data in pages:
                if page_data['has_content'] and page_data['text'].strip():
                    st.markdown(f"""
                    #### Page {page_data['page']}
                    - **Word Count:** {page_data['word_count']}
                    - **Character Count:** {page_data['char_count']}
                    - **Has Content:** ✅
                    
                    **Extracted Text:**
                    ```
                    {page_data['text']}
                    ```
                    """)
                else:
                    st.markdown(f"""
                    #### Page {page_data['page']}
                    - **Has Content:** ❌
                    - **Note:** No text content found on this page
                    """)
        
        # Download option
        if 'pages_data' in result and result['pages_data']:
            if st.button("💾 Download All Extracted Text"):
                all_text = "\n\n".join([
                    f"=== Page {p['page']} ===\n{p['text']}" 
                    for p in result['pages_data'] if p['has_content']
                ])
                st.download_button(
                    label="Download Complete Text",
                    data=all_text,
                    file_name=f"extracted_text_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )

def display_error(response):
    """Display error information from API response"""
    
    st.markdown('<div class="error-box">', unsafe_allow_html=True)
    st.error(f"❌ Error {response.status_code}: Failed to process PDF")
    
    try:
        error_data = response.json()
        
        if 'error' in error_data:
            error_info = error_data['error']
            st.error(f"**Error Code:** {error_info.get('error_code', 'unknown')}")
            st.error(f"**Message:** {error_info.get('message', 'No message available')}")
            
            if 'suggestion' in error_info:
                st.info(f"💡 **Suggestion:** {error_info['suggestion']}")
            
            if 'details' in error_info:
                with st.expander("🔍 Error Details"):
                    st.json(error_info['details'])
        else:
            st.error("Unknown error format received from server")
            
    except json.JSONDecodeError:
        st.error("Invalid response format received from server")
        st.code(response.text)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "Research AI - Document Analysis Tool | Powered by FastAPI & Streamlit"
    "</div>",
    unsafe_allow_html=True
)

if __name__ == "__main__":
    main()
