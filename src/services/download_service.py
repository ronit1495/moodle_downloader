"""Download service for handling file downloads."""

import os
import time
import logging
import urllib.parse
import re
from bs4 import BeautifulSoup
from config.config import BASE_URL, DOWNLOAD_FOLDER
from src.utils.request_utils import safe_request
from src.utils.file_utils import create_folder, get_best_filename, clean_filename

logger = logging.getLogger(__name__)

def get_file_extension_from_url(url):
    """Extract file extension from URL or content type"""
    parsed_url = urllib.parse.urlparse(url)
    path = urllib.parse.unquote(parsed_url.path)
    extension = os.path.splitext(path)[1]
    if extension:
        return extension.lower()
    return ""

def get_file_extension_from_headers(headers):
    """Get file extension from content-type header"""
    content_type = headers.get('content-type', '').lower()
    # Map of common MIME types to extensions
    mime_to_ext = {
        'application/pdf': '.pdf',
        'application/msword': '.doc',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
        'application/vnd.ms-excel': '.xls',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
        'application/vnd.ms-powerpoint': '.ppt',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation': '.pptx',
        'text/plain': '.txt',
        'text/html': '.html',
        'image/jpeg': '.jpg',
        'image/png': '.png',
        'image/gif': '.gif',
        'application/zip': '.zip',
        'application/x-rar-compressed': '.rar',
        'video/mp4': '.mp4',
        'video/quicktime': '.mov',
        'audio/mpeg': '.mp3',
        'application/json': '.json'
    }
    return mime_to_ext.get(content_type, '')

def get_course_name(session, course_id):
    """Get course name from course ID."""
    course_url = f"{BASE_URL}/course/view.php?id={course_id}"
    
    try:
        response = safe_request(session, "GET", course_url)
        if not response:
            logger.error(f"Failed to fetch course page for ID {course_id}")
            return f"Course_{course_id}"
            
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Try to find course name in page title
        title = soup.find("title")
        if title:
            # Split by ':' and take the last part for better course name
            parts = title.text.split(':')
            if len(parts) > 1:
                course_name = parts[-1].strip()
            else:
                course_name = parts[0].strip()
            if course_name:
                return clean_filename(course_name)
                
        # Fallback to h1 heading
        heading = soup.find("h1")
        if heading:
            return clean_filename(heading.text.strip())
            
        # Last resort - use course ID
        return f"Course_{course_id}"
        
    except Exception as e:
        logger.error(f"Error getting course name for ID {course_id}: {str(e)}")
        return f"Course_{course_id}"

def get_actual_file_url(session, view_url):
    """Get the actual file URL from the resource view page."""
    try:
        # Get the resource view page
        response = safe_request(session, "GET", view_url)
        if not response:
            return None
            
        # Parse the page to find the actual file link
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Try different ways to find the file URL
        # 1. Look for resourceworkaround link
        resource_link = soup.find("a", {"class": "resourceworkaround"})
        if resource_link and "href" in resource_link.attrs:
            return resource_link["href"]
            
        # 2. Look for object tag with data attribute
        object_tag = soup.find("object", {"data": True})
        if object_tag:
            return object_tag["data"]
            
        # 3. Look for standard download button
        download_link = soup.find("a", string=re.compile(r"Download|View"))
        if download_link and "href" in download_link.attrs:
            return download_link["href"]
            
        # 4. Look for pluginfile.php in any link
        for link in soup.find_all("a", href=True):
            if "pluginfile.php" in link["href"]:
                return link["href"]
                
        return None
    except Exception as e:
        logger.error(f"Error getting actual file URL: {str(e)}")
        return None

def download_course_files(session, course_id):
    """Download all files from a course"""
    course_url = f"{BASE_URL}/course/view.php?id={course_id}"
    
    try:
        course_name = get_course_name(session, course_id)
        logging.info(f"\nProcessing: {course_name} (ID: {course_id})")
        
        course_folder = os.path.join(DOWNLOAD_FOLDER, clean_filename(course_name))
        create_folder(course_folder)
        
        course_page = safe_request(session, "GET", course_url)
        if not course_page:
            logging.error("Failed to fetch course page")
            return
            
        soup = BeautifulSoup(course_page.text, "html.parser")
        
        # Find all links
        links = soup.find_all("a", href=True)
        logging.debug(f"Found {len(links)} total links in course page")
        
        file_count = 0
        for link in links:
            file_url = link["href"]
            
            if "pluginfile.php" in file_url or "/resource/" in file_url:
                try:
                    # Get filename from different sources
                    file_name = None
                    
                    # 1. Try to get from data-filename attribute if present (most reliable)
                    file_name = link.get('data-filename')
                    
                    # 2. Try to get from the link text if it looks like a filename
                    if not file_name:
                        link_text = link.get_text().strip()
                        if link_text and len(link_text) > 3 and not link_text.startswith('http'):
                            # Check if link text looks like a filename (has extension or reasonable length)
                            if '.' in link_text or len(link_text) > 10:
                                file_name = link_text
                    
                    # 3. Try to get from URL
                    if not file_name:
                        parsed_url = urllib.parse.urlparse(file_url)
                        query = urllib.parse.parse_qs(parsed_url.query)
                        
                        # Check various Moodle URL patterns
                        if 'file' in query:
                            file_name = query['file'][0]
                        elif 'forcedownload' in query:
                            file_name = query['forcedownload'][0]
                        else:
                            # Try the last part of the path after pluginfile.php
                            parts = parsed_url.path.split('pluginfile.php/')
                            if len(parts) > 1:
                                file_name = parts[1].split('/')[-1]
                            else:
                                file_name = parsed_url.path.split('/')[-1]
                    
                    # Ensure we have a valid filename
                    if not file_name or file_name.lower() in ['click', 'download', 'file', 'pluginfile.php']:
                        file_name = f"file_{int(time.time())}_{file_count}"
                    
                    # Clean the base filename
                    file_name = clean_filename(file_name)
                    base_name, existing_ext = os.path.splitext(file_name)
                    
                    # Get file URL
                    if not file_url.startswith("http"):
                        file_url = urllib.parse.urljoin(BASE_URL, file_url)
                    
                    # Make HEAD request to get headers
                    head_response = safe_request(session, "HEAD", file_url)
                    if not head_response:
                        continue
                    
                    # Get extension from multiple sources
                    url_ext = get_file_extension_from_url(file_url)
                    content_ext = get_file_extension_from_headers(head_response.headers)
                    
                    # Choose the best extension (prioritize existing > url > content-type)
                    final_ext = existing_ext
                    if not final_ext or final_ext.lower() == '.php':  # Don't use .php extension
                        final_ext = url_ext if url_ext and url_ext.lower() != '.php' else content_ext
                    
                    # If we still have no extension or it's .php, try to guess from content
                    if not final_ext or final_ext.lower() == '.php':
                        # Make a small GET request to check file signature
                        file_response = safe_request(session, "GET", file_url, stream=True)
                        if file_response:
                            # Read first few bytes to check file signature
                            file_start = next(file_response.iter_content(chunk_size=8), None)
                            if file_start:
                                # PDF signature
                                if file_start.startswith(b'%PDF'):
                                    final_ext = '.pdf'
                                # ZIP signatures
                                elif file_start.startswith(b'PK'):
                                    final_ext = '.zip'
                                # Common image signatures
                                elif file_start.startswith(b'\xFF\xD8'):
                                    final_ext = '.jpg'
                                elif file_start.startswith(b'\x89PNG'):
                                    final_ext = '.png'
                    
                    # Construct final filename with extension
                    final_filename = base_name + (final_ext if final_ext else '')
                    file_path = os.path.join(course_folder, final_filename)
                    
                    # Handle duplicate filenames
                    counter = 1
                    while os.path.exists(file_path):
                        new_filename = f"{base_name}_{counter}{final_ext}"
                        file_path = os.path.join(course_folder, new_filename)
                        counter += 1
                    
                    logging.info(f"Downloading: {os.path.basename(file_path)}")
                    
                    # Download the file
                    file_response = safe_request(session, "GET", file_url, stream=True)
                    if not file_response:
                        continue
                    
                    if file_response.status_code == 200:
                        with open(file_path, "wb") as f:
                            for chunk in file_response.iter_content(chunk_size=8192):
                                if chunk:
                                    f.write(chunk)
                        logging.info(f"Successfully downloaded: {os.path.basename(file_path)}")
                        file_count += 1
                    else:
                        logging.error(f"Failed to download {os.path.basename(file_path)}: {file_response.status_code}")
                
                except Exception as e:
                    logging.error(f"Error downloading file: {str(e)}")
                    continue
        
        logging.info(f"Downloaded {file_count} files from {course_name}")
        
    except Exception as e:
        logging.error(f"Error processing course {course_id}: {str(e)}")

def download_all_courses(session, course_ids):
    """Download files from all courses."""
    logger.info("\nStarting file downloads...")
    
    # Create downloads folder
    create_folder(DOWNLOAD_FOLDER)
    
    # Download files from each course
    for course_id in course_ids:
        download_course_files(session, course_id)
        time.sleep(2)  # Add delay between processing courses
    
    logger.info("\nDownload process completed!") 