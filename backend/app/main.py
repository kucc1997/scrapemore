from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.scraper import fetch_links, scrape_content, extract_unique_categories
from app.schemas import UrlResponse, ContentResponse

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # Adjust as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class URLRequest(BaseModel):
    url: str
    domain: str

class URLListRequest(BaseModel):
    urls: list[str]

class CategoryLink(BaseModel):
    category: str
    link: str

class UrlResponse(BaseModel):
    urls: list[str]
    categories: list[CategoryLink]

class ContentResponse(BaseModel):
    contents: dict


@app.post("/analyze", response_model=UrlResponse)
async def analyze_url(request: URLRequest):
    try:
         # Fetch links from the main URL
        urls = await fetch_links(request.url)
        
        # Extract unique categories from the URLs
        categories = extract_unique_categories(urls)

        # Generate category links
        category_links = [
            {'category': cat, 'link': f"{request.domain}/{cat.lower()}"}
            for cat in categories
        ]
        
        return {"urls": urls, "categories": category_links}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint to scrape content from a list of URLs
@app.post("/scrape", response_model=ContentResponse)
async def scrape_urls(request: URLListRequest):
    try:
        contents = await scrape_content(request.urls)
        return {"contents": contents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))