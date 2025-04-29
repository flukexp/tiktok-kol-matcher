import json
from typing import Dict, Any
import re
import ollama
from utils.logger import logger
from utils.constants import MISTRAL_MODEL

class AIAnalyzer:
    """Module for AI-powered analysis using Mistral-7B from Ollama."""
    
    @staticmethod
    def extract_brand_profile(fb_data: Dict[str, Any], website_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract brand profile from Facebook and website data using Mistral-7B.
        
        Args:
            fb_data: Facebook page data
            website_data: Website data
            
        Returns:
            Dictionary containing brand profile information
        """
        logger.info("Extracting brand profile with Mistral-7B")
        
        try:
            # Prepare the input for the AI model
            fb_text = f"FB Page Name: {fb_data.get('name', '')}\n"
            fb_text += f"About: {fb_data.get('about', '')}\n"
            fb_text += f"Description: {fb_data.get('description', '')}\n"
            fb_text += f"Category: {fb_data.get('category', '')}\n"
            
            # Add posts content
            posts_text = ""
            for post in fb_data.get("posts", []):
                posts_text += f"{post.get('text', '')}\n"
            
            website_text = f"Website Title: {website_data.get('title', '')}\n"
            website_text += f"Meta Description: {website_data.get('meta_description', '')}\n"
            website_text += f"Keywords: {website_data.get('keywords', '')}\n"
            website_text += f"Content Summary: {website_data.get('content', '')[:1000]}\n"
            
            prompt = f"""
            Based on the following Facebook page data and website information, analyze this brand's profile:
            
            FACEBOOK DATA:
            {fb_text}
            
            WEBSITE DATA:
            {website_text}
            
            RECENT FB POSTS:
            {posts_text[:1000]}
            
            Please analyze and return a structured JSON object with the following:
            1. "industry": The primary industry/sector of the business
            2. "target_audience": Description of the likely target audience (age, interests, demographics)
            3. "brand_voice": The tone and style of the brand (professional, casual, playful, etc.)
            4. "key_themes": List of 5-10 key themes and topics that this brand focuses on
            5. "keywords": List of 10-15 keywords that best describe this brand
            
            Return ONLY the JSON object, properly formatted.
            """
            
            # Query Mistral-7B model using Ollama
            response = ollama.chat(
                model=MISTRAL_MODEL,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse the JSON response
            ai_response = response['message']['content']
            
            # Extract JSON content using regex
            json_pattern = r'```json\n(.*?)\n```|```(.*?)```|(\{.*\})'
            json_match = re.search(json_pattern, ai_response, re.DOTALL)
            
            if json_match:
                json_content = json_match.group(1) or json_match.group(2) or json_match.group(3)
                brand_profile = json.loads(json_content)
            else:
                # If no JSON format detected, try to parse the entire response
                try:
                    brand_profile = json.loads(ai_response)
                except:
                    # If all fails, extract data manually
                    lines = ai_response.split("\n")
                    brand_profile = {
                        "industry": "",
                        "target_audience": "",
                        "brand_voice": "",
                        "key_themes": [],
                        "keywords": []
                    }
                    
                    for line in lines:
                        if "industry:" in line.lower():
                            brand_profile["industry"] = line.split(":", 1)[1].strip()
                        elif "target audience:" in line.lower():
                            brand_profile["target_audience"] = line.split(":", 1)[1].strip()
                        elif "brand voice:" in line.lower():
                            brand_profile["brand_voice"] = line.split(":", 1)[1].strip()
                        elif "key themes:" in line.lower() or "themes:" in line.lower():
                            themes_text = line.split(":", 1)[1].strip()
                            brand_profile["key_themes"] = [theme.strip() for theme in themes_text.split(",")]
                        elif "keywords:" in line.lower():
                            keywords_text = line.split(":", 1)[1].strip()
                            brand_profile["keywords"] = [kw.strip() for kw in keywords_text.split(",")]
            
            logger.info("Successfully extracted brand profile with Mistral-7B")
            return brand_profile
            
        except Exception as e:
            logger.error(f"Error extracting brand profile with Mistral-7B: {e}")
            return {
                "industry": "",
                "target_audience": "",
                "brand_voice": "",
                "key_themes": [],
                "keywords": []
            }
    
    @staticmethod
    def analyze_kol_match(brand_profile: Dict[str, Any], kol_details: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the match between a brand and a TikTok KOL using Mistral-7B.
        
        Args:
            brand_profile: Brand profile data
            kol_details: TikTok KOL details
            
        Returns:
            Dictionary containing match analysis
        """
        logger.info(f"Analyzing match between brand and KOL: {kol_details.get('username', '')}")
        
        try:
            # Prepare the input for the AI model
            brand_text = f"Industry: {brand_profile.get('industry', '')}\n"
            brand_text += f"Target Audience: {brand_profile.get('target_audience', '')}\n"
            brand_text += f"Brand Voice: {brand_profile.get('brand_voice', '')}\n"
            brand_text += f"Key Themes: {', '.join(brand_profile.get('key_themes', []))}\n"
            brand_text += f"Keywords: {', '.join(brand_profile.get('keywords', []))}\n"
            
            kol_text = f"Username: {kol_details.get('username', '')}\n"
            kol_text += f"Nickname: {kol_details.get('nickname', '')}\n"
            kol_text += f"Biography: {kol_details.get('biography', '')}\n"
            kol_text += f"Followers: {kol_details.get('followers', 0)}\n"
            kol_text += f"Video Samples: {kol_details.get('video_texts', '')[:1000]}\n"
            
            prompt = f"""
            Based on the following brand profile and TikTok influencer (KOL) data, analyze how well they match:
            
            BRAND PROFILE:
            {brand_text}
            
            TIKTOK KOL PROFILE:
            {kol_text}
            
            Please analyze and return a structured JSON object with the following:
            1. "match_score": A number between 0-100 indicating how well this KOL matches the brand
            2. "audience_fit": Description of how well the KOL's audience aligns with the brand's target audience
            3. "content_alignment": How well the KOL's content style aligns with the brand's themes
            4. "collaboration_potential": Potential types of collaborations that would work well
            5. "match_reasons": List of 2-3 specific reasons why this KOL would be a good match
            6. "cautions": List of 1-2 potential concerns or cautions about this match
            
            Return ONLY the JSON object, properly formatted.
            """
            
            # Query Mistral-7B model using Ollama
            response = ollama.chat(
                model=MISTRAL_MODEL,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse the JSON response
            ai_response = response['message']['content']
            
            # Extract JSON content using regex
            json_pattern = r'```json\n(.*?)\n```|```(.*?)```|(\{.*\})'
            json_match = re.search(json_pattern, ai_response, re.DOTALL)
            
            if json_match:
                json_content = json_match.group(1) or json_match.group(2) or json_match.group(3)
                match_analysis = json.loads(json_content)
            else:
                # If no JSON format detected, try to parse the entire response
                try:
                    match_analysis = json.loads(ai_response)
                except:
                    # If all fails, extract data manually
                    lines = ai_response.split("\n")
                    match_analysis = {
                        "match_score": 0,
                        "audience_fit": "",
                        "content_alignment": "",
                        "collaboration_potential": "",
                        "match_reasons": [],
                        "cautions": []
                    }
                    
                    for line in lines:
                        if "match score:" in line.lower():
                            try:
                                score_text = line.split(":", 1)[1].strip()
                                match_analysis["match_score"] = int(re.search(r'\d+', score_text).group())
                            except:
                                match_analysis["match_score"] = 50
                        elif "audience fit:" in line.lower():
                            match_analysis["audience_fit"] = line.split(":", 1)[1].strip()
                        elif "content alignment:" in line.lower():
                            match_analysis["content_alignment"] = line.split(":", 1)[1].strip()
                        elif "collaboration potential:" in line.lower():
                            match_analysis["collaboration_potential"] = line.split(":", 1)[1].strip()
                        elif "match reasons:" in line.lower() or "reasons:" in line.lower():
                            reasons_text = line.split(":", 1)[1].strip()
                            match_analysis["match_reasons"] = [reason.strip() for reason in reasons_text.split(",")]
                        elif "cautions:" in line.lower() or "concerns:" in line.lower():
                            cautions_text = line.split(":", 1)[1].strip()
                            match_analysis["cautions"] = [caution.strip() for caution in cautions_text.split(",")]
            
            # Ensure match_score is a number
            if isinstance(match_analysis.get("match_score"), str):
                try:
                    match_analysis["match_score"] = int(re.search(r'\d+', match_analysis["match_score"]).group())
                except:
                    match_analysis["match_score"] = 50
            
            logger.info(f"Successfully analyzed match for KOL: {kol_details.get('username', '')}")
            return match_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing KOL match with Mistral-7B: {e}")
            return {
                "match_score": 0,
                "audience_fit": "",
                "content_alignment": "",
                "collaboration_potential": "",
                "match_reasons": [],
                "cautions": []
            }
