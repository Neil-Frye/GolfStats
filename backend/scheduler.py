"""
Scheduler for GolfStats ETL jobs.

This module runs scheduled tasks for the GolfStats application, including
daily ETL processes to fetch data from external sources.
"""
import os
import sys
import logging
import time
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

# Add the project root directory to Python path if not already added
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from config.config import config
from backend.etl.daily_etl import run_daily_etl

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(project_root, 'logs', 'scheduler.log'))
    ]
)
logger = logging.getLogger(__name__)

def create_scheduler() -> BackgroundScheduler:
    """
    Create and configure the scheduler.
    
    Returns:
        Configured BackgroundScheduler instance
    """
    scheduler = BackgroundScheduler()
    
    # Add daily ETL job
    daily_schedule = config["etl"]["schedule"]["daily_update"]
    scheduler.add_job(
        daily_etl_job,
        CronTrigger.from_crontab(daily_schedule),
        id='daily_etl',
        name='Daily ETL Process',
        replace_existing=True
    )
    
    # Add weekly report job (if needed in the future)
    weekly_schedule = config["etl"]["schedule"]["weekly_report"]
    scheduler.add_job(
        weekly_report_job,
        CronTrigger.from_crontab(weekly_schedule),
        id='weekly_report',
        name='Weekly Report Generation',
        replace_existing=True
    )
    
    logger.info(f"Scheduler configured with jobs: daily ETL at '{daily_schedule}', weekly report at '{weekly_schedule}'")
    return scheduler

def daily_etl_job() -> None:
    """
    Run the daily ETL process as a scheduled job.
    """
    try:
        logger.info("Starting scheduled daily ETL job")
        results = run_daily_etl()
        logger.info(f"Daily ETL job completed - Processed {results['users_processed']} users, "
                   f"{results['trackman_sessions']} Trackman sessions, "
                   f"{results['arccos_rounds']} Arccos rounds, "
                   f"{results['skytrak_sessions']} SkyTrak sessions")
    except Exception as e:
        logger.error(f"Error in daily ETL job: {str(e)}")

def weekly_report_job() -> None:
    """
    Generate weekly reports as a scheduled job.
    """
    try:
        logger.info("Starting scheduled weekly report job")
        # TODO: Implement weekly report generation
        logger.info("Weekly report job completed")
    except Exception as e:
        logger.error(f"Error in weekly report job: {str(e)}")

def run_scheduler() -> None:
    """
    Run the scheduler indefinitely.
    """
    scheduler = create_scheduler()
    
    try:
        logger.info("Starting scheduler")
        scheduler.start()
        
        # Keep the process alive
        while True:
            time.sleep(60)
            
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopping due to keyboard interrupt or system exit")
    except Exception as e:
        logger.error(f"Scheduler error: {str(e)}")
    finally:
        scheduler.shutdown()
        logger.info("Scheduler shut down")

if __name__ == "__main__":
    logger.info(f"GolfStats Scheduler starting at {datetime.now()}")
    run_scheduler()