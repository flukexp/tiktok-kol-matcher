from typing import Dict, Any
from apify_client import ApifyClient
from utils.logger import logger
from utils.constants import FACEBOOK_SCRAPER_ACTOR

class FacebookScraper:
    """Module for extracting data from Facebook pages."""
    
    def __init__(self, apify_client: ApifyClient):
        """Initialize the Facebook scraper.
        
        Args:
            apify_client: An initialized ApifyClient instance
        """
        self.apify_client = apify_client
        
    def extract_fb_page_data(self, fb_page_url: str) -> Dict[str, Any]:
        """Extract data from a Facebook page using Apify.
        
        Args:
            fb_page_url: URL of the Facebook page
            
        Returns:
            Dictionary containing extracted Facebook page data
        """
        logger.info(f"Extracting data from Facebook page: {fb_page_url}")
        
        try:
            # Use Apify's Facebook Page Scraper Actor
            run_input = {
                "startUrls": [{"url": fb_page_url}],
                "proxyConfiguration": {"useApifyProxy": True},
                "maxPosts": 20,
                "scrapeAbout": True,
                "scrapePosts": True,
            }
            
            run = self.apify_client.actor(FACEBOOK_SCRAPER_ACTOR).call(run_input=run_input)
            
            # Process the results
            items = self.apify_client.dataset(run["defaultDatasetId"]).list_items().items
            
            if not items:
                logger.warning(f"No data extracted from Facebook page: {fb_page_url}")
                return {}
            
            page_data = items[0]
            
            # Extract relevant information
            processed_data = {
                "name": page_data.get("name", ""),
                "about": page_data.get("about", ""),
                "description": page_data.get("description", ""),
                "category": page_data.get("category", ""),
                "followers": page_data.get("followers", 0),
                "posts": []
            }
            
            # Process posts
            if "posts" in page_data and page_data["posts"]:
                for post in page_data["posts"][:20]:  # Limit to latest 20 posts
                    processed_data["posts"].append({
                        "text": post.get("text", ""),
                        "likes": post.get("likes", 0),
                        "comments": post.get("comments", 0),
                        "shares": post.get("shares", 0),
                    })
            
            logger.info(f"Successfully extracted data from Facebook page: {fb_page_url}")
            return processed_data
            
        except Exception as e:
            logger.error(f"Error extracting data from Facebook page: {e}")
            return {}
