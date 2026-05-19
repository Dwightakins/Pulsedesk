import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List
from datetime import datetime
import logging
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EmailConfig:
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    SENDER = os.getenv('GMAIL_USER')
    PASSWORD = os.getenv('GMAIL_PASSWORD')
    RECIPIENT = os.getenv('RECIPIENT_EMAIL')

class DigestEmailBuilder:
    def __init__(self):
        self.config = EmailConfig()
        self.date_str = datetime.now().strftime('%A, %B %d, %Y')
    
    def _build_html(self, summaries: List, edition: str = "Morning") -> str:
        edition_emoji = "☀️" if edition == "Morning" else "🌙"
        edition_tagline = "Start your day informed" if edition == "Morning" else "Catch up before you clock out"
        
        articles_html = ""
        for i, summary in enumerate(summaries, 1):
            category_colors = {
                'Tech': ('#e3f2fd', '#1565c0'),
                'Business': ('#e8f5e9', '#2e7d32'),
                'Finance': ('#fff3e0', '#e65100'),
                'Entertainment': ('#f3e5f5', '#7b1fa2')
            }
            
            cat = getattr(summary, 'source', '')
            bg_color, text_color = category_colors.get('Tech', ('#f5f5f5', '#333333'))
            
            # Try to detect category from source name
            for cat_name, colors in category_colors.items():
                if hasattr(summary, 'source'):
                    source_lower = summary.source.lower()
                    if cat_name.lower() in source_lower:
                        bg_color, text_color = colors
                        break
            
            articles_html += f"""
            <tr>
                <td style="padding: 20px 30px; border-bottom: 1px solid #eaeaea;">
                    <table width="100%" cellpadding="0" cellspacing="0">
                        <tr>
                            <td>
                                <span style="
                                    display: inline-block;
                                    background: #1a1a2e;
                                    color: #ffffff;
                                    padding: 3px 10px;
                                    border-radius: 12px;
                                    font-size: 11px;
                                    font-weight: 600;
                                    letter-spacing: 0.5px;
                                    margin-bottom: 8px;
                                ">{summary.source.upper()}</span>
                                <span style="
                                    display: inline-block;
                                    background: #e8f5e9;
                                    color: #2e7d32;
                                    padding: 3px 8px;
                                    border-radius: 12px;
                                    font-size: 11px;
                                    font-weight: 600;
                                    margin-left: 6px;
                                ">{summary.relevance_score:.0%} relevant</span>
                            </td>
                        </tr>
                        <tr>
                            <td style="padding-top: 8px;">
                                <a href="{summary.url}" style="
                                    color: #1a1a2e;
                                    text-decoration: none;
                                    font-size: 16px;
                                    font-weight: 700;
                                    line-height: 1.4;
                                ">{summary.title}</a>
                            </td>
                        </tr>
                        <tr>
                            <td style="padding-top: 8px;">
                                <p style="
                                    color: #4a4a4a;
                                    font-size: 14px;
                                    line-height: 1.6;
                                    margin: 0;
                                ">{summary.brief}</p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
            """
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="margin: 0; padding: 0; background-color: #f4f4f8; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
            <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f4f4f8; padding: 20px 0;">
                <tr>
                    <td align="center">
                        <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
                            
                            <!-- Header -->
                            <tr>
                                <td style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); padding: 30px; text-align: center;">
                                    <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: 800; letter-spacing: 1px;">PULSEDESK</h1>
                                    <p style="color: #a8b2d1; margin: 8px 0 0 0; font-size: 14px; letter-spacing: 1px;">{edition_emoji} {edition} Edition</p>
                                    <p style="color: #8892b0; margin: 4px 0 0 0; font-size: 12px; font-style: italic;">{edition_tagline}</p>
                                </td>
                            </tr>
                            
                            <!-- Date Bar -->
                            <tr>
                                <td style="background-color: #f8f9fa; padding: 12px 30px; border-bottom: 2px solid #eaeaea;">
                                    <table width="100%" cellpadding="0" cellspacing="0">
                                        <tr>
                                            <td style="color: #666; font-size: 13px;">{self.date_str}</td>
                                            <td style="color: #666; font-size: 13px; text-align: right;">{len(summaries)} stories curated for you</td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                            
                            <!-- Articles -->
                            {articles_html}
                            
                            <!-- Footer -->
                            <tr>
                                <td style="background-color: #1a1a2e; padding: 25px 30px; text-align: center;">
                                    <p style="color: #a8b2d1; font-size: 12px; margin: 0; line-height: 1.6;">
                                        Powered by PulseDesk | AI-curated business intelligence<br>
                                        Delivered fresh every morning and evening
                                    </p>
                                </td>
                            </tr>
                            
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """
        return html
    
    def build_digest(self, summaries: List, edition: str = "Morning") -> MIMEMultipart:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"PulseDesk {edition} Edition | {self.date_str}"
        msg['From'] = f"PulseDesk <{self.config.SENDER}>"
        msg['To'] = self.config.RECIPIENT
        
        html_content = self._build_html(summaries, edition=edition)
        msg.attach(MIMEText(html_content, 'html'))
        
        return msg

class DigestSender:
    def __init__(self):
        self.config = EmailConfig()
    
    def send(self, message: MIMEMultipart) -> bool:
        try:
            logger.info(f"Connecting to {self.config.SMTP_SERVER}...")
            
            with smtplib.SMTP_SSL(self.config.SMTP_SERVER, 465, timeout=30) as server:
                server.login(self.config.SENDER, self.config.PASSWORD)
                server.send_message(message)
            
            logger.info(f"Digest sent successfully to {self.config.RECIPIENT}")
            return True
        
        except smtplib.SMTPAuthenticationError:
            logger.error("Gmail authentication failed. Check your App Password.")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Failed to send digest: {str(e)}")
            return False


if __name__ == "__main__":
    from scrapers import ArticleAggregator
    from summarizer import ArticleSummarizer
    
    print("Running full PulseDesk pipeline...\n")
    
    # Step 1: Scrape
    print("STEP 1: Scraping sources...")
    aggregator = ArticleAggregator()
    articles = aggregator.get_articles()
    print(f"Scraped {len(articles)} articles\n")
    
    # Step 2: Summarize
    print("STEP 2: Summarizing with Mistral AI...")
    summarizer = ArticleSummarizer()
    summaries = summarizer.summarize_batch(articles)
    filtered = summarizer.filter_by_relevance(summaries, threshold=0.6)
    sorted_summaries = summarizer.sort_by_relevance(filtered)
    print(f"Generated {len(sorted_summaries)} relevant summaries\n")
    
    # Step 3: Build and send email
    print("STEP 3: Building and sending digest...")
    builder = DigestEmailBuilder()
    message = builder.build_digest(sorted_summaries[:8], edition="Evening")
    
    sender = DigestSender()
    success = sender.send(message)
    
    if success:
        print(f"\nDONE! Check {os.getenv('RECIPIENT_EMAIL')} for your digest.")
    else:
        print("\nFailed to send. Check the error above.")
