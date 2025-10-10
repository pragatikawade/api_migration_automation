# utils/util_report.py
import datetime
# utils/report_util.py
from datetime import datetime
from openpyxl import Workbook
import os


# conftest.py or report_util.py
def pytest_configure(config):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    html_path = f"reports/html_reports/api_validation_{timestamp}.html"
    os.makedirs(os.path.dirname(html_path), exist_ok=True)
    config.option.htmlpath = html_path
    config.option.self_contained_html = True  # ✅ embed CSS/JS in the HTML


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    results = []
    for report in terminalreporter.getreports('passed'):
        results.append([report.nodeid, "PASSED", round(report.duration, 2)])
    # Add failed/skipped similarly...

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    os.makedirs("reports/excel_reports", exist_ok=True)
    excel_path = f"reports/excel_reports/api_validation_{timestamp}.xlsx"

    wb = Workbook()
    ws = wb.active
    ws.title = "Test Results"
    ws.append(["Test Name", "Result", "Duration (s)"])
    for row in results:
        ws.append(row)

    wb.save(excel_path)
    terminalreporter.write_sep("=", f"📊 Excel report generated: {excel_path}")
