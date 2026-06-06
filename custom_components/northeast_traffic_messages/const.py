"""Constants for the Northeast Traffic Messages integration."""

DOMAIN = "northeast_traffic_messages"

CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_SIGN_ID = "sign_id"
CONF_FRIENDLY_SIGN_ID = "friendly_sign_id"

API_STATIC_URL = "https://www.netraveldata.co.uk/api/v2/vms/static"
API_DYNAMIC_URL = "https://www.netraveldata.co.uk/api/v2/vms/dynamic"

SCAN_INTERVAL_SECONDS = 5 * 60
STATIC_CACHE_TTL_SECONDS = 24 * 60 * 60

API_RETRY_MAX_ATTEMPTS = 3
API_RETRY_BASE_DELAY_SECONDS = 1

MANUFACTURER = "NECA Tyne & Wear UTMC"
USER_AGENT = "HomeAssistant/NortheastTrafficMessages/1.0.0"

REPO_URL = "https://github.com/06benste/northeasttrafficmessages/"
DOCUMENTATION_URL = REPO_URL
SIGN_LIST_URL = f"{REPO_URL}blob/main/supported_signs.json"

SIGN_SETTING_REASONS = (
    "No Override",
    "Scheduled Override",
    "Group Scheduled Override",
    "Manual Override",
)
