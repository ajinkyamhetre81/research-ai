import streamlit as st
import requests
import io
import base64
import time
from typing import Optional, Dict, Any, List
import json
from datetime import datetime
import pandas as pd

# Configure page
st.set_page_config(
    page_title="Document Processing Hub",
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
DEFAULT_API_URL = "http://localhost:8000"

class DocumentProcessingHub:
    """Unified document processing hub for PDF and website processing."""
    
    def __init__(self):
        self.api_url = DEFAULT_API_URL
    
    def render_header(self):
        """Render the main header."""
        st.markdown('<h1 class="main-header">📄 Document Processing Hub</h1>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("Process PDF documents and scrape websites with advanced extraction capabilities.")
    
    def render_sidebar(self):
        """Render the configuration sidebar."""
        with st.sidebar:
            st.header("⚙️ Configuration")
            
            # API Configuration
            self.api_url = st.text_input(
                "API Base URL", 
                value=DEFAULT_API_URL, 
                help="URL of the FastAPI backend server"
            )
            
            # PDF Processing Options
            st.header("📄 PDF Options")
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
            
            # Website Scraping Options
            st.header("🕷️ Website Options")
            max_pages = st.slider(
                "Maximum Pages",
                min_value=1,
                max_value=500,
                value=50,
                help="Maximum number of pages to crawl"
            )
            
            max_depth = st.slider(
                "Maximum Depth",
                min_value=1,
                max_value=10,
                value=3,
                help="How deep to follow links from the starting page"
            )
            
            concurrency = st.slider(
                "Concurrency",
                min_value=1,
                max_value=10,
                value=1,
                help="Number of concurrent requests (Note: Selenium works best with 1)"
            )
            
            show_content = st.checkbox(
                "Show Full Content",
                value=False,
                help="Display full page content for website scraping"
            )
            
            return {
                "page_range": page_range,
                "languages": languages,
                "max_pages": max_pages,
                "max_depth": max_depth,
                "concurrency": concurrency,
                "show_content": show_content
            }
    
    def render_pdf_processing_tab(self, config):
        """Render PDF processing interface."""
        st.header("📄 PDF Document Processing")
        
        # Processing mode selection
        mode = st.radio(
            "Choose Processing Mode:",
            ["📁 Upload PDF File", "🔗 Process PDF from URL"],
            horizontal=True
        )
        
        if mode == "📁 Upload PDF File":
            self.render_pdf_upload_ui(config)
        else:
            self.render_pdf_url_ui(config)
    
    def render_pdf_upload_ui(self, config):
        """Render PDF upload interface."""
        st.subheader("Upload PDF File")
        
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type=['pdf'],
            help="Upload a PDF document for text extraction and analysis"
        )
        
        if uploaded_file is not None:
            # File info display
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("File Name", uploaded_file.name)
            
            with col2:
                st.metric("File Size", f"{uploaded_file.size / 1024:.1f} KB")
            
            with col3:
                st.metric("File Type", uploaded_file.type)
            
            # Preview
            if st.button("📖 Preview PDF", type="secondary"):
                self.preview_pdf_file(uploaded_file)
            
            # Process button
            if st.button("🚀 Process PDF", type="primary", use_container_width=True):
                with st.spinner("📄 Processing PDF..."):
                    result = self.process_uploaded_pdf(uploaded_file, config)
                
                self.render_pdf_results(result)
    
    def render_pdf_url_ui(self, config):
        """Render PDF URL processing interface."""
        st.subheader("Process PDF from URL")
        
        pdf_url = st.text_input(
            "PDF URL",
            placeholder="https://example.com/document.pdf",
            help="Enter the URL of the PDF file to process"
        )
        
        if pdf_url:
            # URL validation
            if st.button("🔍 Validate URL", type="secondary"):
                self.validate_pdf_url(pdf_url)
            
            # Process button
            if st.button("🚀 Process PDF from URL", type="primary", use_container_width=True):
                with st.spinner("📄 Processing PDF from URL..."):
                    result = self.process_pdf_url(pdf_url, config)
                
                self.render_pdf_results(result)
    
    def preview_pdf_file(self, uploaded_file):
        """Preview PDF file."""
        try:
            # Display PDF preview
            base64_pdf = base64.b64encode(uploaded_file.read()).decode('utf-8')
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="400" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
            uploaded_file.seek(0)  # Reset file pointer
        except Exception as e:
            st.error(f"Error previewing PDF: {str(e)}")
    
    def validate_pdf_url(self, url: str):
        """Validate PDF URL."""
        try:
            response = requests.head(url, timeout=10)
            content_type = response.headers.get('content-type', '')
            
            if 'application/pdf' in content_type:
                st.success("✅ Valid PDF URL detected!")
                st.json({
                    "URL": url,
                    "Content-Type": content_type,
                    "Status Code": response.status_code,
                    "Content-Length": response.headers.get('content-length', 'Unknown')
                })
            else:
                st.error(f"❌ Invalid PDF URL. Content type: {content_type}")
        except Exception as e:
            st.error(f"❌ Error validating URL: {str(e)}")
    
    def process_uploaded_pdf(self, uploaded_file, config) -> Dict[str, Any]:
        """Process uploaded PDF file."""
        try:
            endpoint = f"{self.api_url}/upload-pdf"
            
            files = {'file': (uploaded_file.name, uploaded_file, 'application/pdf')}
            data = {}
            if config.get("page_range"):
                data['page_range'] = config["page_range"]
            if config.get("languages"):
                data['languages'] = config["languages"]
            
            response = requests.post(endpoint, files=files, data=data, timeout=120)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "success": False,
                    "error": f"API Error: {response.status_code} - {response.text}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Processing error: {str(e)}"
            }
    
    def process_pdf_url(self, url: str, config) -> Dict[str, Any]:
        """Process PDF from URL."""
        try:
            endpoint = f"{self.api_url}/process-pdf-url"
            
            request_data = {
                "pdf_url": url,
                "languages": config.get("languages", ['eng'])
            }
            if config.get("page_range"):
                request_data["page_range"] = config["page_range"]
            
            response = requests.post(endpoint, json=request_data, timeout=120)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "success": False,
                    "error": f"API Error: {response.status_code} - {response.text}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Processing error: {str(e)}"
            }
    
    def render_pdf_results(self, result: Dict[str, Any]):
        """Render PDF processing results."""
        if not result.get("success") and not result.get("pages_data"):
            st.error(f"❌ PDF Processing Failed: {result.get('error', 'Unknown error')}")
            return
        
        st.success("✅ PDF Processing Completed Successfully!")
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        
        if 'extraction_summary' in result:
            summary = result['extraction_summary']
            with col1:
                st.metric("Total Pages", summary.get("total_pages", 0))
            with col2:
                st.metric("Total Characters", summary.get("total_characters", 0))
            with col3:
                st.metric("Processing Time", f"{result.get('processing_time_ms', 0):.1f}ms")
        else:
            pages = result.get("pages_data", [])
            with col1:
                st.metric("Total Pages", len(pages))
            with col2:
                total_chars = sum(p.get("char_count", 0) for p in pages)
                st.metric("Total Characters", total_chars)
            with col3:
                st.metric("Pages with Content", sum(1 for p in pages if p.get("has_content", False)))
        
        # Pages data
        pages = result.get("pages_data", [])
        
        if not pages:
            st.warning("No pages were processed.")
            return
        
        st.markdown("---")
        st.subheader("📄 Extracted Pages")
        
        # View options
        view_mode = st.radio(
            "View Mode:",
            ["📊 Table View", "📝 Detailed View", "📥 Download"],
            horizontal=True
        )
        
        if view_mode == "📊 Table View":
            self.render_pdf_table_view(pages)
        elif view_mode == "📝 Detailed View":
            self.render_pdf_detailed_view(pages)
        else:
            self.render_pdf_download_options(pages, result)
    
    def render_pdf_table_view(self, pages: List[Dict]):
        """Render PDF pages in table format."""
        table_data = []
        for i, page in enumerate(pages, 1):
            table_data.append({
                "Page": page.get("page", i),
                "Character Count": page.get("char_count", 0),
                "Word Count": len(page.get("text", "").split()),
                "Has Content": "✅" if page.get("has_content", False) else "❌",
                "Preview": page.get("text", "")[:100] + "..." if len(page.get("text", "")) > 100 else page.get("text", "")
            })
        
        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True)
        
        # Page selection for detailed view
        selected_page = st.selectbox(
            "Select a page to view full text:",
            options=range(len(pages)),
            format_func=lambda i: f"Page {pages[i].get('page', i+1)}"
        )
        
        if selected_page is not None:
            page = pages[selected_page]
            st.subheader(f"Page {page.get('page', selected_page + 1)}")
            st.text_area("Full Text", page.get("text", ""), height=200, disabled=True)
    
    def render_pdf_detailed_view(self, pages: List[Dict]):
        """Render detailed view of all PDF pages."""
        for i, page in enumerate(pages, 1):
            with st.expander(f"📄 Page {page.get('page', i)} ({page.get('char_count', 0)} chars)"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.text_area("Page Content", page.get("text", ""), height=150, disabled=True)
                
                with col2:
                    st.metric("Characters", page.get("char_count", 0))
                    st.metric("Words", len(page.get("text", "").split()))
                    st.metric("Has Content", "✅" if page.get("has_content", False) else "❌")
    
    def render_pdf_download_options(self, pages: List[Dict], result: Dict[str, Any]):
        """Render download options for PDF data."""
        st.subheader("📥 Download Options")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # JSON Download
            json_data = json.dumps(result, indent=2)
            st.download_button(
                label="📄 Download JSON",
                data=json_data,
                file_name=f"pdf_processing_{int(time.time())}.json",
                mime="application/json"
            )
        
        with col2:
            # Text Download
            full_text = "\n\n".join([f"--- Page {p.get('page', i+1)} ---\n{p.get('text', '')}" for i, p in enumerate(pages)])
            st.download_button(
                label="📝 Download Text",
                data=full_text,
                file_name=f"pdf_extracted_text_{int(time.time())}.txt",
                mime="text/plain"
            )
        
        with col3:
            # CSV Download
            csv_data = []
            for page in pages:
                csv_data.append({
                    "Page": page.get("page", ""),
                    "Character_Count": page.get("char_count", 0),
                    "Has_Content": page.get("has_content", False),
                    "Text": page.get("text", "")
                })
            
            df = pd.DataFrame(csv_data)
            csv_string = df.to_csv(index=False)
            st.download_button(
                label="📊 Download CSV",
                data=csv_string,
                file_name=f"pdf_processing_{int(time.time())}.csv",
                mime="text/csv"
            )
    
    def render_website_scraping_tab(self, config):
        """Render website scraping interface."""
        st.header("🕷️ Website Scraping")
        
        # URL input
        url = st.text_input(
            "Website URL",
            placeholder="https://example.com",
            help="Enter the main website URL to crawl"
        )
        
        if not url:
            st.info("👈 Please enter a website URL to start crawling.")
            return
        
        # Crawl button
        if st.button("🚀 Start Crawling", type="primary", use_container_width=True):
            crawl_config = {
                "url": url,
                "max_pages": config["max_pages"],
                "max_depth": config["max_depth"],
                "concurrency": config["concurrency"],
                "show_content": config["show_content"]
            }
            
            with st.spinner("🕷️ Crawling website... This may take a few minutes..."):
                results = self.call_crawl_api(crawl_config)
            
            self.render_website_results(results, crawl_config)
    
    def call_crawl_api(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Call the website crawling API."""
        try:
            payload = {
                "url": config["url"],
                "max_pages": config["max_pages"],
                "max_depth": config["max_depth"],
                "concurrency": config["concurrency"]
            }
            
            response = requests.post(
                f"{self.api_url}/api/crawl-website",
                json=payload,
                timeout=300  # 5 minutes timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "success": False,
                    "error": f"API Error: {response.status_code} - {response.text}"
                }
                
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "Request timed out. The website might be large or slow to respond."
            }
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "error": "Connection error. Please check if the API server is running."
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
    
    def render_website_results(self, results: Dict[str, Any], config: Dict[str, Any]):
        """Render website crawling results."""
        if not results.get("success"):
            st.error(f"❌ Crawling Failed: {results.get('error', 'Unknown error')}")
            return
        
        st.success("✅ Crawling Completed Successfully!")
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Pages Crawled", results.get("total_pages_crawled", 0))
        
        with col2:
            st.metric("Max Pages Requested", config["max_pages"])
        
        with col3:
            success_rate = (results.get("total_pages_crawled", 0) / config["max_pages"]) * 100
            st.metric("Success Rate", f"{success_rate:.1f}%")
        
        # Pages data
        pages = results.get("pages", [])
        
        if not pages:
            st.warning("No pages were crawled. The website might have blocked access or no content was found.")
            return
        
        st.markdown("---")
        st.subheader("📄 Crawled Pages")
        
        # Display format selector
        display_format = st.radio("Display Format:", ["JSON", "Markdown"], horizontal=True)
        
        if display_format == "JSON":
            st.subheader("📊 API Response (JSON)")
            st.json(results)
        else:
            # Original display logic
            view_mode = st.radio(
                "View Mode:",
                ["📊 Table View", "📝 Detailed View", "📥 Download"],
                horizontal=True
            )
            
            if view_mode == "📊 Table View":
                self.render_website_table_view(pages, config)
            elif view_mode == "📝 Detailed View":
                self.render_website_detailed_view(pages, config)
            else:
                self.render_website_download_options(pages, results)
    
    def render_website_table_view(self, pages: List[Dict], config: Dict[str, Any]):
        """Render website pages in table format."""
        table_data = []
        for i, page in enumerate(pages, 1):
            table_data.append({
                "#": i,
                "URL": page.get("url", ""),
                "Title": page.get("title", "")[:50] + "..." if len(page.get("title", "")) > 50 else page.get("title", ""),
                "Content Length": len(page.get("content", "")),
                "Meta Description": page.get("meta_description", "")[:30] + "..." if len(page.get("meta_description", "")) > 30 else page.get("meta_description", "")
            })
        
        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True)
        
        # Page selection for detailed view
        selected_page = st.selectbox(
            "Select a page to view details:",
            options=range(len(pages)),
            format_func=lambda i: f"{i+1}. {pages[i].get('title', 'No title')[:50]}..."
        )
        
        if selected_page is not None:
            self.render_website_page_details(pages[selected_page], config)
    
    def render_website_detailed_view(self, pages: List[Dict], config: Dict[str, Any]):
        """Render detailed view of all website pages."""
        for i, page in enumerate(pages, 1):
            with st.expander(f"📄 {i}. {page.get('title', 'No title')}"):
                self.render_website_page_details(page, config)
    
    def render_website_page_details(self, page: Dict, config: Dict[str, Any]):
        """Render details for a single website page."""
        # Basic Info
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**URL:**")
            st.code(page.get("url", ""), language="text")
        
        with col2:
            st.write("**Meta Description:**")
            st.text(page.get("meta_description", "No meta description"))
        
        # Content
        if config.get("show_content", False):
            st.write("**Content:**")
            content = page.get("content", "")
            if content:
                st.text_area("Full Content", content, height=200, disabled=True)
            else:
                st.info("No content extracted")
    
    def render_website_download_options(self, pages: List[Dict], results: Dict[str, Any]):
        """Render download options for website data."""
        st.subheader("📥 Download Options")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # JSON Download
            json_data = json.dumps(results, indent=2)
            st.download_button(
                label="📄 Download JSON",
                data=json_data,
                file_name=f"website_crawl_{int(time.time())}.json",
                mime="application/json"
            )
        
        with col2:
            # CSV Download
            if pages:
                csv_data = []
                for page in pages:
                    csv_data.append({
                        "URL": page.get("url", ""),
                        "Title": page.get("title", ""),
                        "Meta Description": page.get("meta_description", ""),
                        "Content": page.get("content", "")
                    })
                
                df = pd.DataFrame(csv_data)
                csv_string = df.to_csv(index=False)
                
                st.download_button(
                    label="📊 Download CSV",
                    data=csv_string,
                    file_name=f"website_crawl_{int(time.time())}.csv",
                    mime="text/csv"
                )
        
        with col3:
            # Markdown Download
            if pages:
                markdown_content = self.generate_website_markdown_report(pages, results)
                st.download_button(
                    label="📝 Download Markdown",
                    data=markdown_content,
                    file_name=f"website_crawl_report_{int(time.time())}.md",
                    mime="text/markdown"
                )
    
    def generate_website_markdown_report(self, pages: List[Dict], results: Dict[str, Any]) -> str:
        """Generate a markdown report of the crawled data."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        md_content = f"""# Website Crawling Report

**Generated:** {timestamp}  
**Total Pages Crawled:** {results.get('total_pages_crawled', 0)}  
**Success:** {'Yes' if results.get('success') else 'No'}

---

## Summary

"""
        
        for i, page in enumerate(pages, 1):
            title = page.get('title', 'No title')
            url = page.get('url', '')
            meta_desc = page.get('meta_description', 'No meta description')
            content = page.get('content', '')
            
            md_content += f"""### {i}. {title}

**URL:** {url}

**Meta Description:** {meta_desc}

**Content Preview:** {content[:200]}{'...' if len(content) > 200 else ''}

---
"""
        
        return md_content
    
    def render_footer(self):
        """Render footer with instructions."""
        st.markdown("---")
        
        with st.expander("📖 How to Use"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                ### 📄 PDF Processing
                1. **Upload PDF**: Choose a file or provide URL
                2. **Configure**: Select processing options
                3. **Process**: Click to extract text
                4. **View**: Browse extracted content
                5. **Download**: Export in preferred format
                """)
            
            with col2:
                st.markdown("""
                ### 🕷️ Website Scraping
                1. **Enter URL**: Provide website address
                2. **Configure**: Set crawl limits and depth
                3. **Start**: Begin crawling process
                4. **Monitor**: Track progress in real-time
                5. **Export**: Download results
                """)
            
            st.markdown("""
            **Tips:**
            - For PDFs: Large files may take longer to process
            - For websites: Start with small page limits to test
            - Both tools support multiple export formats
            - Check API server status if connection errors occur
            """)
    
    def run(self):
        """Run the main application."""
        self.render_header()
        config = self.render_sidebar()
        
        # Main content tabs
        pdf_tab, website_tab = st.tabs(["📄 PDF Processing", "🕷️ Website Scraping"])
        
        with pdf_tab:
            self.render_pdf_processing_tab(config)
        
        with website_tab:
            self.render_website_scraping_tab(config)
        
        self.render_footer()


def main():
    """Main function to run the Streamlit app."""
    app = DocumentProcessingHub()
    app.run()


if __name__ == "__main__":
    main()
