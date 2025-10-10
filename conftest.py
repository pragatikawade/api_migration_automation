import os
import json
import base64
import inspect
import logging
from functools import lru_cache
import pytest
import requests
from dotenv import load_dotenv
pytest_plugins = ["utils.report_utils"]

# ==========================================================
# 🔹 Logging Setup
# ==========================================================
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(process)d] [%(levelname)s] %(name)s: %(message)s"
)

# ==========================================================
# 🔹 Environment Loading
# ==========================================================
def load_env(env):
    """Load environment variables from .env.<env> file."""
    env_file_path = os.path.join(os.path.dirname(__file__), f".env.{env}")
    if not os.path.exists(env_file_path):
        pytest.fail(f"Environment file {env_file_path} not found.")
    load_dotenv(env_file_path)
    logger.info(f"Loaded environment file: {env_file_path}")


def pytest_addoption(parser):
    """Add custom command-line option to select environment."""
    parser.addoption("--env", action="store", help="Environment to run test in (dev, qa, svt, uat)")


@pytest.fixture(scope="session", autouse=True)
def load_environment(request):
    """Automatically load environment based on pytest command-line option."""
    env = request.config.getoption("--env") or "dev"
    load_env(env)
    print(f"\n✅ Loaded environment file: .env.{env}")
    print(f"🌍 Running tests in environment: {os.getenv('ENVIRONMENT')}")


# ==========================================================
# 🔹 API Config Fixture
# ==========================================================
@pytest.fixture(scope="session")
def api_config():
    """Load API configuration and credentials from environment variables."""
    headers_str = os.getenv("HEADERS")

    if not headers_str:
        pytest.fail("Environment variable 'HEADERS' is not set or invalid")

    try:
        headers = json.loads(headers_str)
    except json.JSONDecodeError as e:
        pytest.fail(f"Environment variable 'HEADERS' must be valid JSON.\nGot: {headers_str}\nError: {e}")

    return {
        "grant_type": os.getenv("GRANT_TYPE"),
        "headers": headers,
        # OAuth2.0 Details
        "MULESOFT_ACCESS_TOKEN_URL_FOR_OAUTH2_AUTH": os.getenv("MULESOFT_ACCESS_TOKEN_URL_FOR_OAUTH2_AUTH"),
        "MULESOFT_CLIENT_ID": os.getenv("MULESOFT_CLIENT_ID"),
        "MULESOFT_CLIENT_SECRET": os.getenv("MULESOFT_CLIENT_SECRET"),
        "AZURE_ACCESS_TOKEN_URL_FOR_OAUTH2_AUTH": os.getenv("AZURE_ACCESS_TOKEN_URL_FOR_OAUTH2_AUTH"),
        "AZURE_CLIENT_ID": os.getenv("AZURE_CLIENT_ID"),
        "AZURE_CLIENT_SECRET": os.getenv("AZURE_CLIENT_SECRET"),
        # Basic Auth Details
        "MULESOFT_USERNAME": os.getenv("MULESOFT_USERNAME"),
        "MULESOFT_PASSWORD": os.getenv("MULESOFT_PASSWORD"),
        "AZURE_USERNAME": os.getenv("AZURE_USERNAME"),
        "AZURE_PASSWORD": os.getenv("AZURE_PASSWORD"),
        "MULESOFT401_USERNAME": os.getenv("MULESOFT401_USERNAME"),
        "MULESOFT401_PASSWORD": os.getenv("MULESOFT401_PASSWORD"),
        # URLs
        "MULE_URL": os.getenv("MULE_URL"),
        "AZURE_URL": os.getenv("AZURE_URL"),
    }


# ==========================================================
# 🔹 Universal OAuth2 Token Fetcher (Cached)
# ==========================================================
@lru_cache(maxsize=None)
def fetch_access_token_cached(client_id, client_secret, token_url, grant_type, system_name):
    """Cached access token fetcher (per worker)."""
    logger.info(f"Fetching {system_name} token...")
    response = requests.post(token_url, data={
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": grant_type,
    })

    if response.status_code != 200:
        pytest.fail(f"Failed to fetch {system_name} token → {response.status_code}: {response.text}")

    token = response.json().get("access_token")
    if not token:
        pytest.fail(f"No access_token found in {system_name} response → {response.text}")

    return token


def fetch_access_token(api_config, system_name):
    """Wrapper to fetch token safely via cache."""
    fun_name = inspect.currentframe().f_code.co_name
    system_name = system_name.upper()

    token_url = api_config.get(f"{system_name}_ACCESS_TOKEN_URL_FOR_OAUTH2_AUTH")
    client_id = api_config.get(f"{system_name}_CLIENT_ID")
    client_secret = api_config.get(f"{system_name}_CLIENT_SECRET")
    grant_type = api_config["grant_type"]

    if not token_url:
        pytest.skip(f"{fun_name}: No token URL configured for {system_name}. Skipping OAuth test.")

    return fetch_access_token_cached(client_id, client_secret, token_url, grant_type, system_name)


@pytest.fixture(scope="session")
def mulesoft_access_token(api_config):
    return fetch_access_token(api_config, "mulesoft")


@pytest.fixture(scope="session")
def azure_access_token(api_config):
    return fetch_access_token(api_config, "azure")


# ==========================================================
# 🔹 Universal Basic Auth Header Generator
# ==========================================================
def generate_basic_auth_header(api_config, system_name):
    """Generate Basic Auth header for MuleSoft or Azure."""
    system_name = system_name.upper()
    username = api_config.get(f"{system_name}_USERNAME")
    password = api_config.get(f"{system_name}_PASSWORD")

    if not username or not password:
        pytest.skip(f"Missing credentials for {system_name} basic auth.")

    auth_str = f"{username}:{password}"
    auth_bytes = auth_str.encode("utf-8")
    auth_base64 = base64.b64encode(auth_bytes).decode("utf-8")

    header = api_config["headers"].copy()
    header["Authorization"] = f"Basic {auth_base64}"
    return header


@pytest.fixture(scope="session")
def mulesoft_basic_auth_header(api_config):
    return generate_basic_auth_header(api_config, "MULESOFT")


@pytest.fixture(scope="session")
def azure_basic_auth_header(api_config):
    return generate_basic_auth_header(api_config, "AZURE")


@pytest.fixture(scope="session")
def invalid_401_basic_auth_header(api_config):
    """Generate intentionally invalid 401 auth header, skip if creds missing."""
    username = api_config.get("MULESOFT401_USERNAME")
    password = api_config.get("MULESOFT401_PASSWORD")

    if not username or not password:
        pytest.skip("Skipping invalid 401 auth header: missing credentials")

    return generate_basic_auth_header(api_config, "MULESOFT401")


# ==========================================================
# 🔹 OAuth2 Header Fixtures
# ==========================================================
@pytest.fixture(scope="session")
def mulesoft_oauth2_header(api_config, mulesoft_access_token):
    header = api_config["headers"].copy()
    token_type = os.getenv("TOKEN_TYPE", "Bearer")
    header["Authorization"] = f"{token_type} {mulesoft_access_token}"
    return header


@pytest.fixture(scope="session")
def azure_oauth2_header(api_config, azure_access_token):
    header = api_config["headers"].copy()
    token_type = os.getenv("TOKEN_TYPE", "Bearer")
    header["Authorization"] = f"{token_type} {azure_access_token}"
    return header
