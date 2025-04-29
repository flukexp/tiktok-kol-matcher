from typing import Dict, List, Any, Optional, OrderedDict
import re
from apify_client import ApifyClient
from utils.logger import logger
from utils.constants import TIKTOK_SCRAPER_ACTOR

class TikTokScraper:
    """Module for extracting data from TikTok with optimized API usage."""
    
    def __init__(self, apify_client: ApifyClient):
        """Initialize the TikTok scraper.
        
        Args:
            apify_client: An initialized ApifyClient instance
        """
        self.apify_client = apify_client
        self.cache = {}  # Simple caching mechanism to avoid duplicate API calls
    
    def search_thai_kols(self, keywords: List[str], limit: int = 30) -> List[Dict[str, Any]]:
        """Search for Thai TikTok KOLs based on keywords.
        
        Args:
            keywords: List of keywords to search for
            limit: Maximum number of KOLs to retrieve
            
        Returns:
            List of TikTok KOL profiles
        """
        logger.info(f"Searching for Thai TikTok KOLs with keywords: {keywords}")
        all_profiles = OrderedDict()
        unique_usernames = set()  # Track unique usernames to avoid duplicates
        
        # Batch keywords to minimize API calls
        keyword_batches = self._batch_keywords(keywords, batch_size=3)
        
        try:
            for keyword_batch in keyword_batches:
                # Create combined hashtags for more efficient searching
                hashtags = []
                for keyword in keyword_batch:
                    # Clean keyword and create hashtag
                    clean_keyword = keyword.strip().replace(" ", "").lower()
                    if clean_keyword:
                        hashtags.append(clean_keyword)
                        # Add Thai-specific variants
                        hashtags.append(f"{clean_keyword}ไทย")  # Append Thai text
                        hashtags.append(f"{clean_keyword}thailand")
                
                if not hashtags:
                    continue
                    
                # Remove duplicates
                hashtags = list(set(hashtags))
                
                logger.info(f"Searching TikTok with hashtags: {hashtags[:5]}...")
                
                # Single API call for the batch with optimized parameters
                run_input = {
                    "hashtags": hashtags[:10],  # Limit to top 10 hashtags per batch
                    "proxyCountryCode": "TH",  # Use Thai proxy for better results
                    "resultsPerPage": min(10, limit),  
                    "shouldDownloadCovers": False,
                    "shouldDownloadSlideshowImages": False,
                    "shouldDownloadSubtitles": False,
                    "shouldDownloadVideos": False
                }
                
                run = self.apify_client.actor(TIKTOK_SCRAPER_ACTOR).call(run_input=run_input)
                
                # Process the results
                dataset_items = self.apify_client.dataset(run["defaultDatasetId"]).list_items().items
                
                # Extract unique creator profiles from videos
                for item in dataset_items:
                    if len(all_profiles) >= limit:
                        break
                    
                    username = self._extract_username_from_weburl(item.get("webVideoUrl", ""))
                    
                    if username and username not in all_profiles:
                        all_profiles[username] = {
                            "username": username,
                            "nickname": item.get("authorMeta", {}).get("name", ""),
                            "biography": item.get("authorMeta", {}).get("signature", ""),
                            "videos": item.get("authorMeta", {}).get("video", 0),
                            "followers": item.get("authorMeta", {}).get("fans", 0),
                            "likes": item.get("authorMeta", {}).get("heart", ""),
                            "video_texts": item.get("text", ""),
                        }
                
                # Break if we have enough profiles
                if len(all_profiles) >= limit:
                    break
            
            sorted_profiles = sorted(all_profiles.values(), key=lambda x: x["followers"], reverse=True)
            return list(sorted_profiles)[:limit]

        except Exception as e:
            logger.error(f"Error searching for TikTok KOLs: {e}")
            return []
    
    @staticmethod
    def _batch_keywords(keywords: List[str], batch_size: int = 3) -> List[List[str]]:
        """Batch keywords to minimize API calls.
        
        Args:
            keywords: List of keywords to batch
            batch_size: Number of keywords per batch
            
        Returns:
            List of keyword batches
        """
        return [keywords[i:i + batch_size] for i in range(0, len(keywords), batch_size)]
    
    @staticmethod
    def _extract_username_from_weburl(url: str) -> Optional[str]:
        """Extract username from TikTok video URL.
        
        Args:
            url: TikTok video URL
            
        Returns:
            Username or None if not found
        """
        if not url:
            return None
            
        match = re.search(r'@([^/]+)', url)
        return match.group(1) if match else None
    
    
    