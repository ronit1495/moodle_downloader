"""Main entry point for the Moodle Downloader."""

import sys
import os

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logging_utils import setup_logging
from utils.request_utils import create_session
from services.auth_service import login, get_sesskey
from services.course_service import get_course_ids
from services.download_service import download_all_courses

def main():
    """Main function to run the Moodle Downloader."""
    # Set up logging
    logger = setup_logging()
    
    try:
        # Create session with retry logic
        session = create_session()
        
        # Login to Moodle
        if not login(session):
            logger.error("Failed to login. Please check your credentials in config.py")
            return
        
        # Get sesskey for AJAX requests
        sesskey = get_sesskey(session)
        if not sesskey:
            logger.error("Failed to get sesskey")
            return
        
        # Get course IDs (either from arguments or automatically)
        if len(sys.argv) > 1:
            try:
                course_ids = [int(arg) for arg in sys.argv[1:]]
                logger.info(f"Using provided course IDs: {course_ids}")
            except ValueError:
                logger.error("Invalid course IDs provided. Please use numbers only.")
                return
        else:
            course_ids = get_course_ids(session, sesskey)
            if not course_ids:
                return
        
        # Download files from all courses
        download_all_courses(session, course_ids)
        
    except KeyboardInterrupt:
        logger.info("\nDownload interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main() 