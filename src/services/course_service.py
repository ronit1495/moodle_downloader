"""Course service for handling course-related operations."""

import logging
import json
from bs4 import BeautifulSoup
from config.config import BASE_URL
from src.utils.request_utils import safe_request

logger = logging.getLogger(__name__)

def get_course_name(session, course_id):
    """Get course name from course page."""
    course_url = f"{BASE_URL}/course/view.php?id={course_id}"
    logger.debug(f"Fetching course name from: {course_url}")
    
    try:
        course_page = session.get(course_url)
        if course_page.status_code != 200:
            logger.error(f"Failed to fetch course page. Status: {course_page.status_code}")
            return f"Course_{course_id}"
            
        soup = BeautifulSoup(course_page.text, "html.parser")
        title = soup.find("title")
        if title:
            course_name = title.text.strip()
            if ": " in course_name:
                course_name = course_name.split(": ", 1)[1]
            logger.debug(f"Found course name: {course_name}")
            return course_name
            
    except Exception as e:
        logger.error(f"Error getting course name for ID {course_id}: {str(e)}")
    
    return f"Course_{course_id}"

def get_course_ids_from_ajax(session, endpoint, sesskey):
    """Get course IDs from AJAX endpoint."""
    course_ids = set()
    
    try:
        response = safe_request(
            session,
            endpoint["method"],
            endpoint["url"],
            json=endpoint.get("data"),
            headers=endpoint.get("headers", {}),
            params={"sesskey": sesskey}
        )
        
        if response and response.text:
            try:
                data = response.json()
                logger.debug(f"Got JSON response from {endpoint['url']}")
                
                # Try to extract course IDs from the JSON response
                if isinstance(data, list) and len(data) > 0:
                    # Handle array response
                    for item in data:
                        if isinstance(item, dict):
                            if "data" in item:
                                courses = item["data"].get("courses", [])
                            else:
                                courses = [item]
                                
                            for course in courses:
                                course_id = course.get("id")
                                if course_id:
                                    course_ids.add(course_id)
                                    logger.info(f"Found course ID {course_id} from AJAX response")
                
                elif isinstance(data, dict):
                    # Handle object response
                    courses = data.get("courses", [])
                    for course in courses:
                        course_id = course.get("id")
                        if course_id:
                            course_ids.add(course_id)
                            logger.info(f"Found course ID {course_id} from AJAX response")
            
            except json.JSONDecodeError:
                logger.debug("Response was not JSON")
                # Try parsing HTML response
                soup = BeautifulSoup(response.text, "html.parser")
                course_links = soup.find_all("a", href=lambda href: href and "course/view.php?id=" in href)
                for link in course_links:
                    href = link.get("href", "")
                    if "id=" in href:
                        try:
                            course_id = int(href.split("id=")[1].split("&")[0])
                            course_ids.add(course_id)
                            logger.info(f"Found course ID {course_id} from HTML in AJAX response")
                        except ValueError:
                            continue
    
    except Exception as e:
        logger.error(f"Error with endpoint {endpoint['url']}: {str(e)}")
    
    return course_ids

def get_course_ids(session, sesskey):
    """Get all available course IDs."""
    logger.info("Fetching course IDs...")
    
    # Try AJAX endpoints that might contain course data
    ajax_endpoints = [
        # Course overview block AJAX endpoint
        {
            "url": f"{BASE_URL}/lib/ajax/service.php",
            "method": "POST",
            "data": [
                {
                    "index": 0,
                    "methodname": "core_course_get_enrolled_courses_by_timeline_classification",
                    "args": {
                        "offset": 0,
                        "limit": 0,  # 0 means no limit
                        "classification": "all",
                        "sort": "fullname",
                        "customfieldname": "",
                        "customfieldvalue": ""
                    }
                }
            ],
            "headers": {"Content-Type": "application/json"}
        },
        # Alternative endpoint
        {
            "url": f"{BASE_URL}/lib/ajax/service.php",
            "method": "POST",
            "data": [
                {
                    "index": 0,
                    "methodname": "block_myoverview_get_enrolled_courses_by_timeline_classification",
                    "args": {
                        "offset": 0,
                        "limit": 0,
                        "classification": "all",
                        "sort": "fullname"
                    }
                }
            ],
            "headers": {"Content-Type": "application/json"}
        }
    ]
    
    all_course_ids = set()
    for endpoint in ajax_endpoints:
        logger.info(f"\nTrying endpoint: {endpoint['url']}")
        course_ids = get_course_ids_from_ajax(session, endpoint, sesskey)
        all_course_ids.update(course_ids)
    
    # Convert to sorted list
    course_ids = sorted(list(all_course_ids))
    
    if course_ids:
        logger.info(f"\nFound {len(course_ids)} unique course IDs in total:")
        logger.info(f"Course IDs: {course_ids}")
        
        # Save course IDs to a file for reference
        with open("course_ids.txt", "w") as f:
            for course_id in course_ids:
                f.write(f"{course_id}\n")
        logger.info("Course IDs have been saved to course_ids.txt")
    else:
        logger.error("\nNo course IDs found automatically. Please follow these steps to find your course IDs:")
        logger.error("1. Log in to your Moodle")
        logger.error("2. Click on any course to open it")
        logger.error("3. Look at the URL in your browser. It will look like: .../course/view.php?id=XXXX")
        logger.error("4. The number after id= is your course ID")
        logger.error("5. Collect all course IDs you want to download")
        logger.error("\nThen run the script with your course IDs as arguments:")
        logger.error("python moodle_downloader.py COURSE_ID1 COURSE_ID2 ...")
    
    return course_ids 