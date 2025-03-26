"""File handling utilities for the Moodle Downloader."""

import os
import urllib.parse
from config.config import INVALID_FILENAME_CHARS, MIME_TO_EXTENSION, FILE_SIGNATURES

def create_folder(path):
    """Create a folder if it doesn't exist."""
    os.makedirs(path, exist_ok=True)

def clean_filename(filename):
    """Clean filename and ensure it has the correct extension."""
    # Remove invalid characters
    for char in INVALID_FILENAME_CHARS:
        filename = filename.replace(char, '_')
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip('. ')
    
    # Replace multiple spaces with single space
    filename = ' '.join(filename.split())
    
    # Limit filename length (Windows has 255 char limit)
    name, ext = os.path.splitext(filename)
    if len(name) > 200:  # Leave room for extension
        name = name[:200]
    
    return name + ext if ext else name

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

def get_file_extension_from_content(file_start):
    """Get file extension by checking file signature."""
    for signature, extension in FILE_SIGNATURES.items():
        if file_start.startswith(signature):
            return extension
    return ""

def get_best_filename(link, file_url, head_response=None, file_content=None):
    """Get the best possible filename with correct extension."""
    # Get filename from different sources
    file_name = None
    
    # 1. Try to get from data-filename attribute if present (most reliable)
    file_name = link.get('data-filename')
    
    # 2. Try to get from the link text if it looks like a filename
    if not file_name:
        link_text = link.get_text().strip()
        if link_text and len(link_text) > 3 and not link_text.startswith('http'):
            # Check if link text looks like a filename
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
    
    # Clean the filename
    file_name = clean_filename(file_name) if file_name else None
    base_name, existing_ext = os.path.splitext(file_name) if file_name else (None, None)
    
    # Get extension from multiple sources
    url_ext = get_file_extension_from_url(file_url)
    content_ext = get_file_extension_from_headers(head_response.headers) if head_response else ""
    signature_ext = get_file_extension_from_content(file_content) if file_content else ""
    
    # Choose the best extension (prioritize existing > url > content-type > signature)
    final_ext = existing_ext
    if not final_ext or final_ext.lower() == '.php':
        final_ext = url_ext if url_ext and url_ext.lower() != '.php' else content_ext
    if not final_ext or final_ext.lower() == '.php':
        final_ext = signature_ext
    
    # If we still don't have a valid filename, generate one
    if not base_name:
        import time
        base_name = f"file_{int(time.time())}"
    
    return base_name + (final_ext if final_ext else '') 