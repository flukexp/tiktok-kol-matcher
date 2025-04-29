from typing import Dict, Any
import re
import requests
from bs4 import BeautifulSoup
from utils.logger import logger

class WebsiteScraper:
    """Module for extracting data from client websites."""
    
    @staticmethod
    def extract_website_data(website_url: str) -> Dict[str, Any]:
        """Extract text and metadata from a website.
        
        Args:
            website_url: URL of the website to scrape
            
        Returns:
            Dictionary containing extracted website data
        """
        logger.info(f"Extracting data from website: {website_url}")
        
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            
            response = requests.get(website_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Extract relevant content
            title = soup.title.string if soup.title else ""
            
            # Extract meta descriptions
            meta_desc = ""
            meta_tag = soup.find("meta", attrs={"name": "description"})
            if meta_tag and "content" in meta_tag.attrs:
                meta_desc = meta_tag.attrs["content"]
            
            # Extract main text content, excluding scripts, styles, etc.
            for script in soup(["script", "style", "noscript", "header", "footer", "nav"]):
                script.extract()
            
            text_content = soup.get_text(separator=' ', strip=True)
            text_content = re.sub(r'\s+', ' ', text_content).strip()
            
            # Extract keywords from metadata
            keywords = ""
            keywords_tag = soup.find("meta", attrs={"name": "keywords"})
            if keywords_tag and "content" in keywords_tag.attrs:
                keywords = keywords_tag.attrs["content"]
            
            website_data = {
                "title": title,
                "meta_description": meta_desc,
                "keywords": keywords,
                "content": text_content[:5000]  # Limit content length
            }
            
            logger.info(f"Successfully extracted data from website: {website_url}")
            return website_data
            
        except Exception as e:
            logger.error(f"Error extracting data from website: {e}")
            return {
                "title": "",
                "meta_description": "",
                "keywords": "",
                "content": ""
            }
