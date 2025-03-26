"""Configuration settings for the Moodle Downloader."""

import os
import logging

# Moodle Configuration
BASE_URL = os.getenv("MOODLE_URL", "https://moodle.iitb.ac.in")
DASHBOARD_URL = f"{BASE_URL}/my/"
LOGIN_URL = f"{BASE_URL}/login/index.php"
USERNAME = os.getenv("MOODLE_USERNAME", "YOUR_USERNAME")
PASSWORD = os.getenv("MOODLE_PASSWORD", "YOUR_PASSWORD")

# File System Configuration
DOWNLOAD_FOLDER = os.getenv("MOODLE_DOWNLOAD_FOLDER", "moodle_downloads")

# Logging Configuration
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
LOG_LEVEL = logging.INFO  # Changed to INFO for less verbose output

# Request Configuration
RETRY_ATTEMPTS = int(os.getenv("MOODLE_RETRY_ATTEMPTS", "3"))
RETRY_BACKOFF_FACTOR = int(os.getenv("MOODLE_RETRY_BACKOFF", "1"))
RETRY_STATUS_FORCELIST = [429, 500, 502, 503, 504]
REQUEST_DELAY = int(os.getenv("MOODLE_REQUEST_DELAY", "1"))  # seconds

# File Extensions
MIME_TO_EXTENSION = {
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

# File Signatures
FILE_SIGNATURES = {
    b'%PDF': '.pdf',
    b'PK': '.zip',
    b'\xFF\xD8': '.jpg',
    b'\x89PNG': '.png'
}

# Invalid filename characters
INVALID_FILENAME_CHARS = '<>:"/\\|?*' 