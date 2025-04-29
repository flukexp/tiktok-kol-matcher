"""
TikTok KOL Matcher for Thai Market
-----------------------------------
An AI-powered tool that matches businesses with relevant TikTok influencers (KOLs) in Thailand
based on the client's Facebook presence and website content.

Created for Convert Cake Digital Marketing Agency
"""

import os
import argparse
from dotenv import load_dotenv
from utils.constants import DEFAULT_KOL_COUNT
from matcher.matcher import TikTokKOLMatcher
from utils.paths import OUTPUT_DIR

# Load environment variables
os.environ.clear()
load_dotenv()
APIFY_API_KEY = os.getenv("APIFY_API_KEY")

def main():
    """Main entry point for the TikTok KOL Matcher tool."""
    parser = argparse.ArgumentParser(description="TikTok KOL Matcher for Thai Market")
    parser.add_argument("--fb-page", required=True, help="URL of the client's Facebook page")
    parser.add_argument("--website", required=True, help="URL of the client's website")
    parser.add_argument("--output", default=os.path.join(OUTPUT_DIR, "matching_kols.json"), help="Path to output file for results")
    parser.add_argument("--count", type=int, default=DEFAULT_KOL_COUNT, help="Number of KOLs to return")
    parser.add_argument("--api-key", help="Apify API key (optional, can also use APIFY_API_KEY env var)")
    
    args = parser.parse_args()
    
    # Get API key
    api_key = args.api_key or APIFY_API_KEY
    if not api_key:
        raise ValueError("Apify API key is required. Set APIFY_API_KEY environment variable or use --api-key parameter.")
    
    # Initialize and run the matcher
    matcher = TikTokKOLMatcher(api_key)
    matching_kols = matcher.run(args.fb_page, args.website, args.output, args.count)
    
    # Print summary
    print(f"\nFound {len(matching_kols)} matching TikTok KOLs for your brand.")
    print(f"Results saved to {args.output}")
    print(f"Summary report generated at {os.path.join(OUTPUT_DIR, 'summary_report.md')}")


if __name__ == "__main__":
    main()