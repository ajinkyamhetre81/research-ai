# services/website_crawler.py

import asyncio
import sys
import re
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse, urlunparse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from utils.loggers import get_logger, log_with_context, log_operation_start, log_operation_end

# Fix Windows compatibility
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class WebsiteCrawler:
    """JavaScript-enabled web crawler using Selenium."""
    
    def __init__(self, max_pages=200, max_depth=3, concurrency=1):
        self.max_pages = max_pages
        self.max_depth = max_depth
        self.concurrency = concurrency  # Note: Selenium doesn't support true concurrency
        self.visited = set()
        self.results = []
        self.base_domain = None
        self.driver = None
        self.logger = get_logger(__name__)
        
        log_with_context(
            self.logger,
            f"Initialized WebsiteCrawler with max_pages={max_pages}, max_depth={max_depth}, concurrency={concurrency}",
            level="INFO",
            extra_context={
                "max_pages": max_pages,
                "max_depth": max_depth,
                "concurrency": concurrency
            }
        )
        
    def _get_domain(self, url):
        """Extract domain from URL."""
        try:
            domain = urlparse(url).netloc
            self.logger.debug(f"Extracted domain '{domain}' from URL '{url}'")
            return domain
        except Exception as e:
            self.logger.error(f"Error extracting domain from URL '{url}': {str(e)}")
            return ""
    
    def _normalize_url(self, url):
        """Normalize URL by removing fragments."""
        try:
            parsed = urlparse(url)
            netloc = parsed.netloc.replace("www.", "")
            path = parsed.path.rstrip("/")
            normalized = urlunparse((parsed.scheme, netloc, path, "", "", ""))
            self.logger.debug(f"Normalized URL: '{url}' -> '{normalized}'")
            return normalized
        except Exception as e:
            self.logger.error(f"Error normalizing URL '{url}': {str(e)}")
            return url
    
    def _setup_driver(self):
        """Setup Chrome driver with headless options."""
        log_operation_start(self.logger, "Chrome driver setup")
        
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            log_with_context(
                self.logger,
                "Configuring Chrome options",
                level="DEBUG",
                extra_context={
                    "headless": True,
                    "window_size": "1920x1080",
                    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
            )
            
            # Use webdriver-manager to automatically handle chromedriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            log_operation_end(self.logger, "Chrome driver setup", True, "Chrome driver setup successful")
            return True
            
        except Exception as e:
            log_operation_end(self.logger, "Chrome driver setup", False, f"Error setting up Chrome driver: {str(e)}")
            self.logger.error(f"Chrome driver setup failed. Please ensure Chrome browser is installed.")
            return False
    
    def _extract_content(self, html, url):
        """Extract main content from HTML."""
        try:
            log_with_context(
                self.logger,
                f"Extracting content from HTML",
                level="DEBUG",
                extra_context={
                    "url": url,
                    "html_length": len(html)
                }
            )
            
            soup = BeautifulSoup(html, 'lxml')
            
            # Remove noise elements
            noise_tags = ['script', 'style', 'noscript', 'iframe', 'nav', 'footer', 'header', 'aside']
            removed_count = 0
            for tag in noise_tags:
                elements = soup.find_all(tag)
                for element in elements:
                    element.decompose()
                    removed_count += 1
            
            self.logger.debug(f"Removed {removed_count} noise elements from HTML")
            
            # Extract title
            title = ""
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.get_text(strip=True)
                self.logger.debug(f"Extracted title: '{title[:50]}{'...' if len(title) > 50 else ''}'")
            
            # Extract meta description
            meta_desc = ""
            meta_tag = soup.find('meta', attrs={'name': 'description'})
            if meta_tag:
                meta_desc = meta_tag.get('content', '').strip()
                self.logger.debug(f"Extracted meta description: '{meta_desc[:100]}{'...' if len(meta_desc) > 100 else ''}'")
            
            # Try to find main content area
            main_content = ""
            content_selectors = ['main', 'article', '[role="main"]', '.content', '#content', '.post-content', '.entry-content']
            
            for selector in content_selectors:
                main_elem = soup.select_one(selector)
                if main_elem:
                    main_content = main_elem.get_text(separator=' ', strip=True)
                    self.logger.debug(f"Found main content using selector: '{selector}'")
                    break
            
            # Fallback to body if no main content found
            if not main_content:
                body = soup.find('body')
                if body:
                    main_content = body.get_text(separator=' ', strip=True)
                    self.logger.debug("Using body content as fallback")
            
            # Clean up text
            main_content = re.sub(r'\s+', ' ', main_content).strip()
            
            # Extract links
            links = []
            for a_tag in soup.find_all('a', href=True):
                href = a_tag.get('href')
                if href and not href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                    next_url = urljoin(url, href)
                    normalized_url = self._normalize_url(next_url)
                    if self._is_valid_internal_link(normalized_url):
                        links.append(normalized_url)
            
            self.logger.debug(f"Extracted {len(links)} valid internal links")
            
            result = {
                "url": url,
                "title": title,
                "meta_description": meta_desc,
                "content": main_content,
                "links": list(set(links))
            }
            
            log_with_context(
                self.logger,
                f"Content extraction completed",
                level="DEBUG",
                extra_context={
                    "url": url,
                    "title_length": len(title),
                    "content_length": len(main_content),
                    "links_found": len(links),
                    "has_meaningful_content": len(main_content) > 50
                }
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error extracting content from {url}: {str(e)}", exc_info=True)
            return None
    
    def _is_valid_internal_link(self, url):
        """Check if URL is a valid internal link."""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.replace("www.", "")
            
            if not domain.endswith(self.base_domain):
                self.logger.debug(f"URL '{url}' rejected: domain '{domain}' does not match base domain '{self.base_domain}'")
                return False
            
            if url in self.visited:
                self.logger.debug(f"URL '{url}' rejected: already visited")
                return False
            
            # Skip non-HTML files
            blocked_extensions = (
                '.pdf', '.jpg', '.jpeg', '.png', '.gif', '.svg',
                '.zip', '.rar', '.tar', '.gz',
                '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
                '.mp4', '.avi', '.mov', '.mp3', '.wav'
            )
            
            if parsed.path.lower().endswith(blocked_extensions):
                self.logger.debug(f"URL '{url}' rejected: blocked file extension")
                return False
            
            self.logger.debug(f"URL '{url}' accepted as valid internal link")
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating internal link '{url}': {str(e)}")
            return False
    
    async def crawl(self, start_url: str):
        """Crawl website starting from given URL."""
        start_time = time.time()
        log_operation_start(self.logger, "Website crawl", f"URL: {start_url}")
        
        # Normalize and validate start URL
        if not start_url.startswith(('http://', 'https://')):
            start_url = 'https://' + start_url
            self.logger.info(f"Added HTTPS scheme to URL: {start_url}")
        
        parsed = urlparse(start_url)
        self.base_domain = parsed.netloc.replace("www.", "")
        
        if not self.base_domain:
            log_operation_end(self.logger, "Website crawl", False, "Invalid URL provided")
            return {
                "success": False,
                "error": "Invalid URL provided",
                "total_pages_crawled": 0,
                "pages": []
            }
        
        log_with_context(
            self.logger,
            f"Starting crawl with configuration",
            level="INFO",
            extra_context={
                "start_url": start_url,
                "base_domain": self.base_domain,
                "max_pages": self.max_pages,
                "max_depth": self.max_depth,
                "concurrency": self.concurrency
            }
        )
        
        # Setup Selenium driver
        if not self._setup_driver():
            log_operation_end(self.logger, "Website crawl", False, "Failed to setup Chrome driver")
            return {
                "success": False,
                "error": "Failed to setup Chrome driver. Please ensure Chrome browser is installed.",
                "total_pages_crawled": 0,
                "pages": []
            }
        
        try:
            # Initialize crawling
            to_crawl = [(start_url, 0)]  # (url, depth)
            pages_processed = 0
            total_links_found = 0
            
            while to_crawl and len(self.results) < self.max_pages:
                current_batch = []
                batch_size = min(self.concurrency, len(to_crawl))
                
                for _ in range(batch_size):
                    if to_crawl:
                        current_batch.append(to_crawl.pop(0))
                
                self.logger.info(f"Processing batch of {len(current_batch)} URLs (depth {current_batch[0][1] if current_batch else 'N/A'})")
                
                # Process current batch
                for url, depth in current_batch:
                    if url in self.visited or depth > self.max_depth:
                        continue
                    
                    if len(self.results) >= self.max_pages:
                        break
                    
                    self.visited.add(url)
                    pages_processed += 1
                    
                    try:
                        log_with_context(
                            self.logger,
                            f"Crawling page",
                            level="INFO",
                            extra_context={
                                "url": url,
                                "depth": depth,
                                "pages_processed": pages_processed,
                                "pages_found": len(self.results),
                                "max_pages": self.max_pages
                            }
                        )
                        
                        page_start_time = time.time()
                        
                        # Load page with JavaScript
                        self.driver.get(url)
                        
                        # Wait for page to load
                        WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.TAG_NAME, "body"))
                        )
                        
                        # Extra wait for dynamic content
                        await asyncio.sleep(2)
                        
                        # Get rendered HTML
                        html = self.driver.page_source
                        page_load_time = time.time() - page_start_time
                        
                        self.logger.debug(f"Page loaded in {page_load_time:.2f} seconds, HTML length: {len(html)}")
                        
                        # Extract content
                        extract_start_time = time.time()
                        page_data = self._extract_content(html, url)
                        extract_time = time.time() - extract_start_time
                        
                        if page_data and len(page_data['content']) > 50:
                            self.results.append({
                                "url": url,
                                "title": page_data['title'],
                                "meta_description": page_data['meta_description'],
                                "content": page_data['content']
                            })
                            
                            # Add links for next depth
                            if depth < self.max_depth:
                                new_links = page_data['links'][:20]  # Limit links per page
                                for link in new_links:
                                    to_crawl.append((link, depth + 1))
                                total_links_found += len(new_links)
                            
                            log_with_context(
                                self.logger,
                                f"Page crawled successfully",
                                level="INFO",
                                extra_context={
                                    "url": url,
                                    "title": page_data['title'][:50] + ('...' if len(page_data['title']) > 50 else ''),
                                    "content_length": len(page_data['content']),
                                    "links_found": len(page_data['links']),
                                    "page_load_time": page_load_time,
                                    "extract_time": extract_time,
                                    "total_results": len(self.results)
                                }
                            )
                        else:
                            self.logger.warning(f"Page skipped: {url} - no meaningful content found")
                    
                    except Exception as e:
                        self.logger.error(f"Error crawling {url}: {str(e)}", exc_info=True)
                
                # Small delay between batches
                if to_crawl:
                    self.logger.debug(f"Waiting 1 second before next batch...")
                    await asyncio.sleep(1)
            
            processing_time = time.time() - start_time
            
            log_operation_end(
                self.logger,
                "Website crawl",
                True,
                f"completed {len(self.results)} pages in {processing_time:.2f} seconds"
            )
            
            log_with_context(
                self.logger,
                f"Crawl summary",
                level="INFO",
                extra_context={
                    "total_pages_crawled": len(self.results),
                    "pages_processed": pages_processed,
                    "total_links_found": total_links_found,
                    "processing_time": processing_time,
                    "avg_time_per_page": processing_time / pages_processed if pages_processed > 0 else 0,
                    "success_rate": (len(self.results) / pages_processed * 100) if pages_processed > 0 else 0
                }
            )
            
        except Exception as e:
            log_operation_end(self.logger, "Website crawl", False, f"unexpected error: {str(e)}")
            self.logger.error(f"Website crawl failed: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"Crawling failed: {str(e)}",
                "total_pages_crawled": 0,
                "pages": []
            }
        
        finally:
            if self.driver:
                self.logger.info("Closing Chrome driver...")
                self.driver.quit()
                self.logger.debug("Chrome driver closed successfully")
        
        return {
            "success": True,
            "total_pages_crawled": len(self.results),
            "pages": self.results
        }