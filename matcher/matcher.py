import os
import json
from typing import Dict, List, Any
from apify_client import ApifyClient
from scraper.facebook import FacebookScraper
from scraper.tiktok import TikTokScraper
from scraper.website import WebsiteScraper
from utils.logger import logger
from analyzer.mistral import AIAnalyzer
from matcher.engine import MatchingEngine
from utils.paths import OUTPUT_DIR
from utils.constants import DEFAULT_KOL_COUNT

class TikTokKOLMatcher:
    """Main class for the TikTok KOL Matcher tool."""
    
    def __init__(self, apify_api_key: str):
        """Initialize the TikTok KOL Matcher.
        
        Args:
            apify_api_key: Apify API key
        """
        
        self.apify_client = ApifyClient(apify_api_key)
        self.fb_scraper = FacebookScraper(self.apify_client)
        self.website_scraper = WebsiteScraper()
        self.tiktok_scraper = TikTokScraper(self.apify_client)
        self.ai_analyzer = AIAnalyzer()
        self.matching_engine = MatchingEngine(self.tiktok_scraper, self.ai_analyzer)
    
    def run(self, fb_page_url: str, website_url: str, output_file: str, kol_count: int = DEFAULT_KOL_COUNT) -> List[Dict[str, Any]]:
        """Run the TikTok KOL Matcher workflow.
        
        Args:
            fb_page_url: URL of the client's Facebook page
            website_url: URL of the client's website
            output_file: Path to output file for results
            kol_count: Number of KOLs to return
            
        Returns:
            List of matching KOL profiles
        """
        logger.info("Starting TikTok KOL Matcher workflow")
        
        # Step 1: Extract Facebook data
        fb_data = self.fb_scraper.extract_fb_page_data(fb_page_url)
        
        # Step 2: Extract website data
        website_data = self.website_scraper.extract_website_data(website_url)
        
        # Step 3: Analyze brand profile
        brand_profile = self.ai_analyzer.extract_brand_profile(fb_data, website_data)
        
        # Save brand profile
        brand_profile_file = os.path.join(OUTPUT_DIR, "brand_profile.json")
        with open(brand_profile_file, "w", encoding="utf-8") as f:
            json.dump(brand_profile, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Brand profile saved to {brand_profile_file}")
        
        # Step 4: Find matching KOLs
        matching_kols = self.matching_engine.find_matching_kols(brand_profile, kol_count)
        
        # Step 5: Save results
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(matching_kols, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Matching KOLs saved to {output_file}")
        
        # Generate summary report
        report_file = os.path.join(OUTPUT_DIR, "summary_report.md")
        self._generate_report(brand_profile, matching_kols, report_file)
        
        logger.info(f"Summary report generated at {report_file}")
        
        return matching_kols
    
    @staticmethod
    def _generate_report(brand_profile: Dict[str, Any], matching_kols: List[Dict[str, Any]], output_file: str) -> None:
        """Generate a summary report of the KOL matching results.
        
        Args:
            brand_profile: Brand profile information
            matching_kols: List of matching KOL profiles
            output_file: Path to output file for report
        """
        report = [
            "# TikTok KOL Matcher Results",
            "",
            "## Brand Profile",
            f"**Industry:** {brand_profile.get('industry', 'N/A')}",
            f"**Target Audience:** {brand_profile.get('target_audience', 'N/A')}",
            f"**Brand Voice:** {brand_profile.get('brand_voice', 'N/A')}",
            "",
            "### Key Themes",
            "".join([f"- {theme}\n" for theme in brand_profile.get("key_themes", [])]),
            "",
            "### Keywords",
            "".join([f"- {keyword}\n" for keyword in brand_profile.get("keywords", [])]),
            "",
            "## Top Matching TikTok KOLs",
            ""
        ]
        
        for i, kol in enumerate(matching_kols[:10], 1):
            report.extend([
                f"### {i}. {kol.get('nickname', kol.get('username', 'Unknown'))}",
                f"**Username:** [@{kol.get('username', 'N/A')}](https://www.tiktok.com/@{kol.get('username', 'N/A')})",
                f"**Match Score:** {kol.get('match_score', 0)}/100",
                f"**Followers:** {kol.get('followers', 0):,}",
                f"**Engagement Likes Per Video:** {kol.get('engagement_avg_likes_per_video', 0):.2f} likes",
                f"**Engagement Likes Per 100 Followers:** {kol.get('engagement_likes_per_100_followers', 0):.2f} likes",
                f"**Bio:** {kol.get('biography', 'N/A')}",
                "",
                "**Why This KOL Matches:**",
                "".join([f"- {reason}\n" for reason in kol.get("match_reasons", [])]),
                "",
                "**Potential Collaborations:**",
                f"{kol.get('collaboration_potential', 'N/A')}",
                "",
                "**Cautions:**",
                "".join([f"- {caution}\n" for caution in kol.get("cautions", [])]),
                "---",
                ""
            ])
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(report))
