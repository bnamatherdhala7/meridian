from dotenv import load_dotenv
import os

load_dotenv()


def get(key: str, required: bool = True) -> str:
    val = os.getenv(key)
    if required and not val:
        raise EnvironmentError(
            f"Missing required env var: {key}\n"
            f"Check .env.example for setup instructions."
        )
    return val or ""


SPLUNK_URL     = get("SPLUNK_URL",     required=False)
SPLUNK_TOKEN   = get("SPLUNK_TOKEN",   required=False)
SPLUNK_MCP_URL = get("SPLUNK_MCP_URL", required=False)

PINECONE_API_KEY        = get("PINECONE_API_KEY")
PINECONE_SPL_INDEX      = get("PINECONE_SPL_INDEX")
PINECONE_INCIDENT_INDEX = get("PINECONE_INCIDENT_INDEX")
PINECONE_ENVIRONMENT    = get("PINECONE_ENVIRONMENT")

OPENAI_API_KEY    = get("OPENAI_API_KEY")
ANTHROPIC_API_KEY = get("ANTHROPIC_API_KEY")

CI_CATALYST_URL   = get("CI_CATALYST_URL",   required=False)
CI_CATALYST_TOKEN = get("CI_CATALYST_TOKEN", required=False)

USE_MOCK_CI = not CI_CATALYST_URL
