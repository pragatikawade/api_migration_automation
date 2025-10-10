import pytest
import time
import logging
from utils.send_request import make_api_request
from utils.compare_API_responses import compare_json_schemas, compare_xml_tags
from utils.send_request import timed_request
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")



@pytest.mark.api
@pytest.mark.positive
def test_001_valid_request_200_OK(mulesoft_basic_auth_header, azure_basic_auth_header, api_config):
    mule_url = api_config["MULE_URL"]
    azure_url = api_config["AZURE_URL"]
    params = {"id": "211"}
    response_time_threshold = 0.5  # seconds

    # -------------------------------
    # MuleSoft
    # -------------------------------
    mule_resp, mule_time = timed_request("GET", mule_url, mulesoft_basic_auth_header, params)
    logger.info(f"MuleSoft → Status: {mule_resp.status_code} | Time: {mule_time:.3f}s | Authenticated: {mule_resp.json().get('authenticated')}")

    # -------------------------------
    # Azure
    # -------------------------------
    azure_resp, azure_time = timed_request("GET", azure_url, azure_basic_auth_header, params)
    logger.info(f"Azure     → Status: {azure_resp.status_code} | Time: {azure_time:.3f}s | Authenticated: {azure_resp.json().get('authenticated')}")

    # -------------------------------
    # 1️⃣    Status Code Comparison
    # -------------------------------
    if mule_resp.status_code == azure_resp.status_code:
        logger.info(f"✅ Status code check passed: {mule_resp.status_code}")
    else:
        logger.error(f"❌ Status code mismatch: MuleSoft={mule_resp.status_code}, Azure={azure_resp.status_code}")
        pytest.fail(f"Status code mismatch: MuleSoft={mule_resp.status_code}, Azure={azure_resp.status_code}")

    # -------------------------------
    # 2️⃣   Response Time Comparison
    # -------------------------------
    diff = abs(mule_time - azure_time)
    if diff <= response_time_threshold:
        logger.info(f"✅ Response time within threshold: MuleSoft={mule_time:.3f}s, Azure={azure_time:.3f}s")
    else:
        logger.warning(f"⚠️ Response time difference > {response_time_threshold}s: MuleSoft={mule_time:.3f}s, Azure={azure_time:.3f}s")

    # -------------------------------
    # 3️⃣   Schema Validation
    # -------------------------------
    content_type = mule_resp.headers.get("Content-Type", "").lower()
    try:
        if "application/json" in content_type:
            assert compare_json_schemas(mule_resp.json(), azure_resp.json()), "JSON schema mismatch"
            logger.info("✅ JSON schema validation passed")
        elif "xml" in content_type:
            assert compare_xml_tags(mule_resp.text, azure_resp.text), "XML tag mismatch"
            logger.info("✅ XML schema validation passed")
        else:
            logger.warning(f"⚠️ Unknown Content-Type: {content_type}. Schema validation skipped")
    except AssertionError as e:
        logger.error(f"❌ {e}")
        pytest.fail(f"Schema validation failed: {e}")

    logger.info("🎯 MuleSoft vs Azure API comparison completed\n")
