# schemas/website_schemas.py

from pydantic import BaseModel
from typing import List


class WebsiteCrawlRequest(BaseModel):
    url: str
    max_pages: int = 100
    max_depth: int = 3
    concurrency: int = 5


class PageData(BaseModel):
    url: str
    title: str
    meta_description: str
    content: str


class WebsiteCrawlResponse(BaseModel):
    success: bool
    total_pages_crawled: int
    pages: List[PageData]