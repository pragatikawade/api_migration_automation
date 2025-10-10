import pytest
import time
import logging
from utils.send_request import timed_request
from utils.compare_API_responses import compare_json_schemas, compare_xml_tags

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")


@pytest.mark.api
@pytest.mark.negative
def test_003_with_invalid_url_endpoint_404_not_found(
    mulesoft_basic_auth_header, azure_basic_auth_header, api_config
):
    mule_url = api_config["MULE_URL"] + "test404"
    azure_url = api_config["AZURE_URL"] + "test404"
    params = {"id": "211"}
    response_time_threshold = 0.5  # seconds

    # -------------------------------
    # MuleSoft request
    # -------------------------------
    mule_resp, mule_time = timed_request("GET", mule_url, mulesoft_basic_auth_header, params)
    mule_text = mule_resp.text.strip()
    try:
        mule_json = mule_resp.json()
    except Exception:
        mule_json = None
    logger.info(f"MuleSoft → Status: {mule_resp.status_code} | Time: {mule_time:.3f}s | Response: {mule_text}")

    # -------------------------------
    # Azure request
    # -------------------------------
    azure_resp, azure_time = timed_request("GET", azure_url, azure_basic_auth_header, params)
    azure_text = azure_resp.text.strip()
    try:
        azure_json = azure_resp.json()
    except Exception:
        azure_json = None
    logger.info(f"Azure     → Status: {azure_resp.status_code} | Time: {azure_time:.3f}s | Response: {azure_text}")

    # -------------------------------
    # 1️⃣  Status Code Comparison
    # -------------------------------
    if mule_resp.status_code == azure_resp.status_code:
        logger.info(f"✅ Status code check passed: {mule_resp.status_code}")
    else:
        logger.error(f"❌ Status code mismatch: MuleSoft={mule_resp.status_code}, Azure={azure_resp.status_code}")
        pytest.fail(f"Status code mismatch: MuleSoft={mule_resp.status_code}, Azure={azure_resp.status_code}")

    # -------------------------------
    # 2️⃣  Response Time Comparison
    # -------------------------------
    diff = abs(mule_time - azure_time)
    if diff <= response_time_threshold:
        logger.info(f"✅ Response time within threshold: MuleSoft={mule_time:.3f}s, Azure={azure_time:.3f}s")
    else:
        logger.warning(f"⚠️ Response time difference > {response_time_threshold}s: MuleSoft={mule_time:.3f}s, Azure={azure_time:.3f}s")

    # -------------------------------
    # 3️⃣  Schema / Raw Text Validation
    # -------------------------------
    try:
        content_type = mule_resp.headers.get("Content-Type", "").lower()
        if mule_json and azure_json:
            # JSON schema validation
            assert compare_json_schemas(mule_json, azure_json), "JSON schema mismatch"
            logger.info("✅ JSON schema validation passed")
        elif "xml" in content_type:
            # XML tag validation
            assert compare_xml_tags(mule_resp.text, azure_resp.text), "XML tag mismatch"
            logger.info("✅ XML schema validation passed")
        else:
            # Raw text validation (for 404, 401, plain text responses)
            assert mule_text == azure_text, f"Raw text mismatch: MuleSoft={mule_text}, Azure={azure_text}"
            logger.info(f"✅ Raw text validation passed: {mule_text}")
    except AssertionError as e:
        logger.error(f"❌ {e}")
        pytest.fail(f"Schema/Text validation failed: {e}")

    logger.info("🎯 MuleSoft vs Azure API comparison completed\n")
