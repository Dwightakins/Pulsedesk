import schedule
import time
import logging
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('pulsedesk.log', encoding='utf-8')
    ]
)
logger = logging.getLogger('pulsedesk')

from scrapers import ArticleAggregator
from summarizer import ArticleSummarizer
from email_sender import DigestEmailBuilder, DigestSender


class PulseDesk:
    def __init__(self):
        self.aggregator = ArticleAggregator()
        self.summarizer = ArticleSummarizer()
        self.email_builder = DigestEmailBuilder()
        self.email_sender = DigestSender()
        self.run_count = 0
    
    def run_digest(self):
        """Execute the full digest pipeline"""
        self.run_count += 1
        start_time = datetime.now()
        
        logger.info(f"{'='*60}")
        logger.info(f"PULSEDESK RUN #{self.run_count} - {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"{'='*60}")
        
        try:
            # Step 1: Scrape
            logger.info("STEP 1: Scraping sources...")
            articles = self.aggregator.get_articles()
            logger.info(f"Scraped {len(articles)} articles")
            
            if not articles:
                logger.warning("No articles scraped. Skipping digest.")
                return False
            
            # Step 2: Summarize
            logger.info("STEP 2: Summarizing with Mistral AI...")
            summaries = self.summarizer.summarize_batch(articles)
            filtered = self.summarizer.filter_by_relevance(summaries, threshold=0.6)
            sorted_summaries = self.summarizer.sort_by_relevance(filtered)
            logger.info(f"Generated {len(sorted_summaries)} relevant summaries")
            
            if not sorted_summaries:
                logger.warning("No relevant summaries generated. Skipping digest.")
                return False
            
            # Step 3: Build and send
            logger.info("STEP 3: Building and sending digest...")
            message = self.email_builder.build_digest(sorted_summaries[:8])
            success = self.email_sender.send(message)
            
            elapsed = (datetime.now() - start_time).seconds
            
            if success:
                logger.info(f"Digest delivered in {elapsed}s | {len(articles)} scraped | {len(sorted_summaries)} summarized")
                return True
            else:
                logger.error(f"Digest failed after {elapsed}s")
                return False
        
        except Exception as e:
            logger.error(f"Pipeline error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def start_scheduler(self, send_time: str = "07:00"):
        """Schedule daily digest at specified time"""
        schedule.every().day.at(send_time).do(self.run_digest)
        
        logger.info(f"PulseDesk scheduler started")
        logger.info(f"Digest scheduled for {send_time} daily")
        logger.info(f"Recipient: {os.getenv('RECIPIENT_EMAIL')}")
        logger.info(f"Press Ctrl+C to stop\n")
        
        try:
            while True:
                schedule.run_pending()
                next_run = schedule.next_run()
                if next_run:
                    time_left = next_run - datetime.now()
                    hours, remainder = divmod(int(time_left.total_seconds()), 3600)
                    minutes, seconds = divmod(remainder, 60)
                    sys.stdout.write(f"\rNext digest in: {hours:02d}h {minutes:02d}m {seconds:02d}s")
                    sys.stdout.flush()
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("\nScheduler stopped by user")


def main():
    print("""
    ╔═══════════════════════════════════════════════╗
    ║              PULSEDESK v1.0                   ║
    ║     AI-Powered Daily Intelligence Digest      ║
    ╚═══════════════════════════════════════════════╝
    """)
    
    pulse = PulseDesk()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--now":
            print("Running digest immediately...\n")
            pulse.run_digest()
        
        elif sys.argv[1] == "--schedule":
            send_time = sys.argv[2] if len(sys.argv) > 2 else "07:00"
            pulse.start_scheduler(send_time)
        
        elif sys.argv[1] == "--help":
            print("Usage:")
            print("  py main.py --now              Run digest immediately")
            print("  py main.py --schedule          Schedule daily at 07:00")
            print("  py main.py --schedule 09:00    Schedule daily at custom time")
            print("  py main.py --help              Show this help")
    else:
        print("What would you like to do?\n")
        print("  1. Send digest now")
        print("  2. Schedule daily digest (default: 7:00 AM)")
        print("  3. Schedule at custom time")
        print("")
        
        choice = input("Enter choice (1/2/3): ").strip()
        
        if choice == "1":
            pulse.run_digest()
        elif choice == "2":
            pulse.start_scheduler("07:00")
        elif choice == "3":
            custom_time = input("Enter time (HH:MM, 24hr format): ").strip()
            pulse.start_scheduler(custom_time)
        else:
            print("Invalid choice")


if __name__ == "__main__":
    main()