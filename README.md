# API Migration Automation

This is a Python project for automated API testing using **pytest**. The project validates API endpoints, checks responses, and generates reports in Excel and HTML formats.

## Project Structure
```
api-migration-automation/
│
├── .venv/ # Virtual environment (Python dependencies)│
├── reports/ # Generated reports
│ ├── excel_reports/ # Excel-based reports
│ ├── html_reports/ # HTML-based reports
│ └── response_data/ # Data files related to API responses
│
├── tests/ # Unit and integration tests
│
├── utils/ # Utility scripts
│ ├── init.py # Marks utils as a package
│ ├── compare_API_responses.py # Compares API responses
│ ├── report_utils.py # Utility functions for reports
│ └── send_request.py # Sends API requests
│
├── .env.dev # Development environment settings
├── .env.qa # QA environment settings
├── .env.svt # Staging environment settings
├── .env.uat # UAT environment settings
├── pytest.ini # pytest configuration file
└── README.md # Project documentation

```
## Setup
1. Clone the repository:
2. git clone <repository-url>
3. cd api_migration_automation 
4. python -m venv api_venv >> source api_env/bin/activate
5. pip install -r requirements.txt
6. pytest -s /tests/test_001_valid_request_200_OK --env=dev


## Reports
Excel reports: reports/excel_reports/
HTML reports: reports/html_reports/
CSS assets for HTML reports: reports/html_reports/assets/style.css

## Utils
send_request.py → Handles API requests
report_utils.py → Generates reports
compare_API_responses.py → Compares API responses for validation

