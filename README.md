# Moodle Downloader

A Python script to automatically download all files from your Moodle courses.

## Author
- **Name:** Ronit Kumar
- **Email:** kumarronit1495@gmail.com
- **LinkedIn:** [Ronit Kumar](https://www.linkedin.com/in/ronit-kumar-4bb343114/)

## License
This software is licensed under the MIT License with the following additional conditions:
- This software is for educational purposes only
- Only to be used by students with active Moodle access
- Not for commercial use
- Must be used for fair purposes and not piracy

## Security Guidelines

⚠️ **IMPORTANT: Before pushing to git or making your repository public:**

1. **Never commit sensitive information:**
   - Moodle credentials
   - Institution-specific URLs
   - Personal course IDs
   - Downloaded course materials

2. **Files to exclude from git:**
   ```
   moodle_downloads/
   course_ids.txt
   debug_*.json
   __pycache__/
   *.pyc
   .env
   ```

3. **Using credentials safely:**
   - Use environment variables (recommended)
   - Never hardcode credentials
   - Keep credentials in a separate, non-committed file

4. **Before each commit:**
   - Remove downloaded materials
   - Remove course_ids.txt
   - Remove debug files
   - Check for sensitive data in comments

## Features

- Automatic course detection
- Downloads all available files from courses
- Smart file extension detection
- Proper file organization by course
- Retry mechanism for failed downloads
- Console progress updates
- Environment variable support for configuration

## Important Notes

### Usage Guidelines
1. This tool is intended for:
   - Students with active Moodle access
   - Personal educational use only
   - Downloading your own course materials
   
2. This tool is NOT for:
   - Commercial use
   - Distribution of copyrighted materials
   - Unauthorized access to course materials

### Contributing
Contributions are welcome! Please feel free to submit a Pull Request. For major changes:
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Git Guidelines
Before committing:
1. Add `moodle_downloads/` to your `.gitignore`
2. Remove any downloaded course materials
3. Never commit personal credentials
4. Remove any debug files

### Issues and Support
- Please report bugs and request features through the [GitHub Issues](https://github.com/yourusername/moodle_downloader/issues) tab
- Provide detailed information when reporting issues:
  - Your operating system
  - Python version
  - Error messages
  - Steps to reproduce

## Setup

1. Clone this repository:
```bash
git clone <repository-url>
cd moodle_downloader
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your Moodle credentials using one of these methods:

### Method 1: Environment Variables (Recommended)

Set the following environment variables based on your operating system:

#### Note: Example of moodle url: https://lms.institute_name.ac.in/

#### Linux/macOS:
```bash
# Add these to your ~/.bashrc, ~/.zshrc, or equivalent
export MOODLE_URL="https://your-moodle-url" 
export MOODLE_USERNAME="your-username"
export MOODLE_PASSWORD="your-password"
```

#### Windows (Command Prompt):
```cmd
set MOODLE_URL=https://your-moodle-url
set MOODLE_USERNAME=your-username
set MOODLE_PASSWORD=your-password
```

#### Windows (PowerShell):
```powershell
$env:MOODLE_URL="https://your-moodle-url"
$env:MOODLE_USERNAME="your-username"
$env:MOODLE_PASSWORD="your-password"
```

### Method 2: Direct Configuration

Edit `config/config.py` and update the default values:
```python
BASE_URL = "https://your-moodle-url"
USERNAME = "your-username"
PASSWORD = "your-password"
```

### Optional Environment Variables

You can also configure these optional settings:
```bash
MOODLE_DOWNLOAD_FOLDER="custom_downloads"  # Default: "moodle_downloads"
MOODLE_RETRY_ATTEMPTS="5"                  # Default: "3"
MOODLE_RETRY_BACKOFF="2"                  # Default: "1"
MOODLE_REQUEST_DELAY="2"                  # Default: "1"
```

## Usage

1. Run without arguments to download from all available courses:
```bash
python src/main.py
```

2. Or specify course IDs to download from specific courses:
```bash
python src/main.py COURSE_ID1 COURSE_ID2
```

Example:
```bash
python src/main.py 1234 5678
```

## File Organization

Files are downloaded to the `moodle_downloads` directory (or your custom directory), organized by course:
```
moodle_downloads/
├── Course_Name_1/
│   ├── file1.pdf
│   ├── file2.docx
│   └── ...
├── Course_Name_2/
│   ├── file1.pdf
│   └── ...
└── ...
```

## Troubleshooting

1. If automatic course detection fails:
   - Log in to your Moodle
   - Click on any course
   - Look at the URL: `.../course/view.php?id=XXXX`
   - The number after id= is your course ID
   - Use these IDs as arguments: `python src/main.py XXXX`

2. If downloads fail:
   - Check your Moodle credentials (environment variables or config.py)
   - Verify your internet connection
   - Check the console output for error messages

3. Environment Variables not working:
   - Make sure you've set them in the correct shell/terminal
   - On Windows, you might need to restart your terminal
   - On Linux/macOS, try `source ~/.bashrc` or `source ~/.zshrc`
   - Verify with: `echo $MOODLE_USERNAME` (Linux/macOS) or `echo %MOODLE_USERNAME%` (Windows CMD) 

## Disclaimer
This software is provided "as is", without warranty of any kind. The authors are not responsible for any misuse of this software or any violations of institutional policies. Users are responsible for ensuring their use complies with their institution's policies and terms of service.

---
Made with ❤️ by [Ronit Kumar](https://www.linkedin.com/in/ronit-kumar-4bb343114/) 