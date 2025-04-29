from typing import Dict, List, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils.logger import logger
from utils.constants import DEFAULT_KOL_COUNT
from analyzer.mistral import AIAnalyzer
from scraper.tiktok import TikTokScraper

class MatchingEngine:
    """Module for matching brands with TikTok KOLs."""
    
    def __init__(self, scraper: TikTokScraper, analyzer: AIAnalyzer):
        """Initialize the matching engine.
        
        Args:
            scraper: TikTokScraper instance
            analyzer: AIAnalyzer instance
        """
        self.scraper = scraper
        self.analyzer = analyzer
        self.vectorizer = TfidfVectorizer(stop_words='english')
    
    def find_matching_kols(self, brand_profile: Dict[str, Any], limit: int = DEFAULT_KOL_COUNT) -> List[Dict[str, Any]]:
        """Find matching TikTok KOLs for a brand.
        
        Args:
            brand_profile: Brand profile information
            limit: Maximum number of KOLs to return
            
        Returns:
            List of matching KOL profiles with scores
        """
        logger.info(f"Finding matching KOLs for brand")
        
        # Extract keywords for TikTok search
        search_keywords = []
        search_keywords.extend(brand_profile.get("keywords", [])[:5])
        search_keywords.append(brand_profile.get("industry", ""))
        search_keywords.extend(brand_profile.get("key_themes", [])[:3])
        
        # Clean and filter keywords
        search_keywords = [kw for kw in search_keywords if kw and len(kw) > 2]
        search_keywords = list(set(search_keywords))  # Remove duplicates
        
        logger.info(f"Using search keywords: {search_keywords}")
        
        # Search for potential KOLs
        potential_kols = self.scraper.search_thai_kols(search_keywords, limit * 3)
        
        # Filter KOLs by minimum requirements
        filtered_kols = []
        processed_usernames = set()  # To avoid duplicates
        
        for kol in potential_kols:
            username = kol.get("username", "")
                
            processed_usernames.add(username)
            
            total_likes = kol.get("likes", 0)
            total_videos = kol.get("videos", 1)  # avoid division by zero
            followers = kol.get("followers", 0) or 1  

            # Calculate simple engagement metric
            avg_likes_per_video = total_likes / total_videos

            # Calculate normalized engagement: likes per 100 followers
            likes_per_100_followers = (total_likes / followers) * 100
            
            # Analyze match with brand
            match_analysis = self.analyzer.analyze_kol_match(brand_profile, kol)
            
            # Calculate additional text similarity
            brand_text = " ".join(brand_profile.get("keywords", []) + brand_profile.get("key_themes", []))
            kol_text = f"{kol.get('biography', '')} {kol.get('video_texts', '')}"
            
            text_similarity = 0
            if brand_text and kol_text:
                try:
                    texts = [brand_text, kol_text]
                    tfidf_matrix = self.vectorizer.fit_transform(texts)
                    text_similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
                except:
                    text_similarity = 0
                    
            # Add a small bonus based on engagement, Cap bonus at 50 to prevent weird cases
            engagement_bonus = min(likes_per_100_followers, 50)  
            
            # Combine scores
            ai_score = match_analysis.get("match_score", 0)
            combined_score = 0.65 * ai_score + 0.25 * (text_similarity * 100) + 0.10 * engagement_bonus
            
            # Create final KOL match info
            kol_match = {
                "username": username,
                "url": f"https://www.tiktok.com/@{username}",
                "nickname": kol.get("nickname", ""),
                "biography": kol.get("biography", ""),
                "followers": kol.get("followers", 0),
                "match_score": round(combined_score, 1),
                "engagement_avg_likes_per_video": round(avg_likes_per_video, 2),
                "engagement_likes_per_100_followers": round(likes_per_100_followers, 2),
                "audience_fit": match_analysis.get("audience_fit", ""),
                "content_alignment": match_analysis.get("content_alignment", ""),
                "collaboration_potential": match_analysis.get("collaboration_potential", ""),
                "match_reasons": match_analysis.get("match_reasons", []),
                "cautions": match_analysis.get("cautions", [])
            }
            
            filtered_kols.append(kol_match)
        
        # Sort by match score
        sorted_kols = sorted(filtered_kols, key=lambda k: k["match_score"], reverse=True)
        
        # Return top matches
        return sorted_kols[:limit]
