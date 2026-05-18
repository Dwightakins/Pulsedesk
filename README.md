# PulseDesk

AI-powered daily intelligence digest that scrapes, summarizes, and delivers curated news to your inbox every morning.

Built with Python, Mistral AI, and BeautifulSoup.

## What It Does

PulseDesk runs on a schedule, scrapes selected news sources across business, tech, and art, feeds everything through Mistral AI to summarize and rank by relevance, then formats it into a clean branded email and delivers it to subscribers.

You open your inbox at 7am and instead of checking multiple websites, everything you need to know is already there.

## Architecture

| File | Role |
|------|------|
| scrapers.py | Concurrent web scraping from 5+ sources |
| summarizer.py | Mistral AI summarization and relevance scoring |
| email_sender.py | HTML email builder and SMTP delivery |
| main.py | Pipeline orchestrator with scheduler |

## Sources

- Nairametrics (Nigerian business and finance)
- BusinessDay Nigeria (Nigerian economy and policy)
- TechPoint Africa (African tech ecosystem)
- Artnews (Global art market)
- Art Africa Magazine (African art and culture)

## Setup

**1. Clone the repo**

    git clone https://github.com/dwightakins/pulsedesk.git
    cd pulsedesk

**2. Install dependencies**

    pip install -r requirements.txt

**3. Create a .env file in the project root**

    GMAIL_USER=your_gmail@gmail.com
    GMAIL_PASSWORD=your_gmail_app_password
    RECIPIENT_EMAIL=recipient@gmail.com
    MISTRAL_API_KEY=your_mistral_api_key

To get a Gmail App Password: Go to myaccount.google.com > Security > App passwords > Create one for PulseDesk.

To get a Mistral API key: Go to console.mistral.ai and generate one.

**4. Run immediately**

    python main.py --now

**5. Schedule daily delivery**

    python main.py --schedule 07:00

## How It Works

1. **Scrape** - Concurrent requests to all sources with retry logic and timeout handling
2. **Summarize** - Mistral AI processes raw articles, extracts key insights, and scores relevance (0-1)
3. **Filter** - Only articles above 60% relevance make the digest
4. **Format** - Professional HTML email template with source badges and relevance indicators
5. **Deliver** - SMTP delivery via Gmail with error handling and logging

## Tech Stack

- Python 3.10+
- BeautifulSoup4 (web scraping)
- Mistral AI API (summarization)
- SMTP (email delivery)
- Schedule (task scheduling)
- Concurrent futures (parallel scraping)

## Usage

    python main.py --now              Send digest immediately
    python main.py --schedule         Schedule daily at 07:00
    python main.py --schedule 09:00   Schedule at custom time
    python main.py --help             Show help

## License

MIT