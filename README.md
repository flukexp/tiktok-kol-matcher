# TikTok KOL Matcher for the Thai Market

An AI-driven solution developed for Convert Cake Digital Marketing Agency to automate the identification and matching of TikTok influencers (KOLs) in Thailand with client businesses based on their Facebook presence and website content.

## Overview

The **TikTok KOL Matcher** streamlines the influencer discovery process by:

1. Analyzing a client's Facebook page and website to understand brand identity, audience, and content style.
2. Identifying and evaluating relevant TikTok influencers in Thailand.
3. Leveraging AI to rank influencers based on brand relevance, engagement metrics, and audience compatibility.
4. Generating a curated, ranked list of recommended TikTok KOLs, accompanied by detailed analytics and collaboration insights.

This solution enhances Convert Cake's influencer marketing services, helping businesses efficiently and strategically expand their TikTok presence.

---

## Features

- **Data Extraction**: Scrapes Facebook pages and websites using Apify actors.
- **Thai Influencer Identification**: Searches TikTok for Thai-based KOLs matching target criteria.
- **AI Analysis**: Utilizes the Mistral-7B model for deep brand and influencer content analysis.
- **Engagement Metrics Calculation**: Assesses follower counts, engagement rates.
- **Scoring and Ranking**: Computes compatibility scores to prioritize influencer recommendations.
- **Report Generation**: Produces structured JSON and Markdown reports with collaboration suggestions and cautions.

---

## Prerequisites

- Python 3.8+
- Apify account with API key
- Ollama installed with the Mistral-7B model
- Active internet connection

---

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/flukexp/tiktok-kol-matcher.git
   cd tiktok-kol-matcher
   ```

2. **Set up a virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Install Ollama (if not already installed):**  
   Instructions: [https://ollama.ai/download](https://ollama.ai/download)

5. **Pull the Mistral-7B model:**

   ```bash
   ollama pull mistral:7b
   ```

6. **Configure environment variables:**

   Create a `.env` file:

   ```
   APIFY_API_KEY=your_apify_api_key_here
   ```

---

## Requirements

Dependencies listed in `requirements.txt`:

```
apify-client==1.3.1
beautifulsoup4==4.12.2
numpy==1.24.3
pandas==2.0.3
python-dotenv==1.0.0
requests==2.31.0
scikit-learn==1.3.0
ollama==0.1.5
```

---

## Usage

### CLI Usage Example

```bash
python main.py --fb-page "https://www.facebook.com/convertcake" --website "https://convertcake.com" --count 10
```

### Command-Line Arguments

- `--fb-page` (required): Facebook page URL of the client.
- `--website` (required): Website URL of the client.
- `--count` (optional): Number of influencer matches to return (default: 10).
- `--output` (optional): Path to save the output JSON file.
- `--api-key` (optional): Apify API key (if not set via `.env`).

### Output

The program generates:

- A **JSON file** with detailed influencer recommendations.
- A **brand profile analysis** file.
- A **Markdown summary report** highlighting top matches and collaboration suggestions.

---

## Project Structure

```
tiktok-kol-matcher/
├── main.py
├── requirements.txt
├── .env
├── output/
│   ├── matching_kols.json
│   ├── brand_profile.json
│   └── summary_report.md
├── matcher/
│   ├── matcher.py
│   ├── engine.py
├── scraper/
│   ├── facebook.py
│   ├── tiktok.py
│   ├── website.py
├── utils/
│   ├── constants.py
│   ├── logger.py
│   ├── paths.py
├── analyzer/
│   ├── mistral.py
```

---

## How It Works

1. **Data Collection**  
   - Extracts Facebook and website data using Apify.
   - Searches for TikTok influencers based on target demographics and keywords.

2. **Brand Analysis**  
   - AI analyzes brand tone, audience, and key themes using Mistral-7B.

3. **Influencer Analysis**  
   - Fetches influencer metrics: follower counts, engagement rates.

4. **Matching Algorithm**  
   - Combines text similarity and demographic matching into a weighted score.

5. **Result Generation**  
   - Produces a ranked list of influencers with full analytics and recommendations.

---

## System Architecture

```
Client Input (FB page URL + Website URL)
        ↓
[Data Collection Layer]
 - Facebook Scraper (Apify)
 - Website Scraper (BeautifulSoup)
 - TikTok Scraper (Apify)
        ↓
[Data Preprocessing Layer]
 - Metadata Extraction
        ↓
[AI Analysis Layer]
 - Brand Analysis (Mistral-7B)
 - Influencer Profile Analysis
        ↓
[Matching Engine]
 - Content Similarity Scoring
 - Engagement Scoring
 - Weighted Ranking Algorithm
        ↓
[Output Layer]
 - JSON: Matching KOLs
 - JSON: Brand Profile
 - Markdown: Summary Report
```

---

## Example Report Contents

- Brand analysis summary
- Top TikTok KOLs, including:
  - TikTok profile links
  - Match scores
  - Reasons for match
  - Collaboration ideas
  - Cautions or risks

---

## External Resources

- **Facebook Scraper Actor**:  
  [https://apify.com/apify/facebook-pages-scraper](https://apify.com/apify/facebook-pages-scraper)

- **TikTok Scraper Actor**:  
  [https://apify.com/clockworks/tiktok-scraper](https://apify.com/clockworks/tiktok-scraper)

---

## License

This project is licensed under the MIT License — see the LICENSE file for full details.

---

### Process Flow

| Phase                  | Details |
|-------------------------|---------|
| **Input**               | FB Page URL, Website URL |
| **Data Collection**     | Scrape FB Page & Website |
| **Data Preprocessing**  | Merge + clean brand metadata |
| **AI Analysis**         | Analyze brand profile using Mistral |
| **Influencer Search**   | Scrape TikTok KOLs using Apify |
| **Matching Engine**     | Content Similarity + AI Match Analysis |
| **Scoring & Ranking**   | Weighted ranking (65% AI, 25% Text Sim, 10% Engagement) |
| **Output**              | Save results in JSON and Markdown |


### Summary of Key Components in Code:

| Module             | Functionality |
|--------------------|---------------|
| `FacebookScraper`  | FB page scraping |
| `WebsiteScraper`   | Website scraping |
| `AIAnalyzer`       | Mistral-7B based profile extraction and match analysis |
| `TikTokScraper`    | TikTok user searching |
| `MatchingEngine`   | Match TikTok KOLs with brands |
| `TikTokKOLMatcher` | Orchestration of the entire workflow |