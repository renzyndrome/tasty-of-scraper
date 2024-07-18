import schedule
import time
import logging
from main import App

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def run_start_scraping():
    logger.info("Starting scheduled scraping task")
    app = App()
    app.start_scraping_silent()
    logger.info("Scheduled scraping task completed")


# Schedule the start_scraping function to run at a specific time
schedule.every().day.at("04:13").do(run_start_scraping)

if __name__ == "__main__":
    logger.info("Scheduler started")
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute
        logger.debug("Checking for scheduled tasks")
