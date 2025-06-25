# Clinic Pipeline

A web scraping pipeline for extracting patient data from a clinic management system.

## Features

- **Web Scraping**: Automated data extraction using Selenium WebDriver
- **Logging**: Comprehensive logging system with file rotation
- **Data Processing**: Clean and structure extracted patient data
- **Configuration**: Environment-based configuration management

## Project Structure

```
clinic-pipeline/
├── src/
│   ├── main.py           # Main application entry point
│   ├── scraper.py        # Web scraping functionality
│   ├── utils.py          # Utility functions for data processing
│   └── logger_config.py  # Logging configuration
├── logs/                 # Log files directory
├── samples/              # Sample data files
├── pyproject.toml        # Project dependencies and configuration
└── LOGGING.md           # Logging documentation
```

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   # or if using uv:
   uv sync
   ```

2. **Configure environment**:
   Create a `.env` file with your credentials:
   ```
   URL=your_clinic_url
   USERNAME_=your_username
   PASSWORD_=your_password
   ```

3. **Install ChromeDriver**:
   Make sure you have Chrome and ChromeDriver installed for Selenium automation.

## Usage

Run the main scraper:

```bash
python src/main.py
```

## Logging

The application uses a structured logging system that outputs to both console and rotating log files. See [LOGGING.md](LOGGING.md) for detailed information about the logging configuration.

## Dependencies

- **selenium**: Web automation
- **python-dotenv**: Environment configuration
- **webdriver-manager**: ChromeDriver management

## Output

Extracted patient data is saved as JSON files with timestamps:
- Format: `patient_data_YYYYMMDD_HHMMSS.json`
- Location: Project root directory
