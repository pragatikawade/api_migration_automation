# ==========================================================
# 🔹 Universal Dynamic API Request Function
# ==========================================================
import logging
import requests
logger = logging.getLogger(__name__)


def make_api_request(method, url, headers, payload=None, files=None):
    method = method.upper()
    content_type = headers.get("Content-Type", "").lower()
    logger.info(f"🔹 {method} {url} | Payload: {payload} | Headers: {headers}")

    if method == "GET":
        response = requests.get(url, headers=headers, params=payload)
    elif method == "DELETE":
        response = requests.delete(url, headers=headers, json=payload if "json" in content_type else None)
    else:
        if "application/json" in content_type:
            response = requests.request(method, url, headers=headers, json=payload)
        else:
            response = requests.request(method, url, headers=headers, data=payload)

    # Safe response logging\
    try:
        resp_content = response.json()
    except Exception:
        resp_content = response.text

    logger.info(f"🔹 Status: {response.status_code} | Response: {resp_content}")
    return response


# utils/send_request.py
import time

def timed_request(method, url, headers, params=None, payload=None, files=None):
    """
    Sends an API request and returns response + elapsed time.
    """
    start = time.perf_counter()
    resp = make_api_request(method, url, headers, payload or params, files)
    elapsed = time.perf_counter() - start
    return resp, elapsed
