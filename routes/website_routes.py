# routes/website_routes.py

from fastapi import APIRouter, HTTPException
from services.website_crawler import WebsiteCrawler
from schemas.website_schemas import (
    WebsiteCrawlRequest,
    WebsiteCrawlResponse
)

router = APIRouter()


@router.post("/crawl-website", response_model=WebsiteCrawlResponse)
async def crawl_website(request: WebsiteCrawlRequest):

    try:
        crawler = WebsiteCrawler(
            max_pages=request.max_pages,
            max_depth=request.max_depth,
            concurrency=request.concurrency
        )

        result = await crawler.crawl(request.url)

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Crawling failed: {str(e)}"
        )