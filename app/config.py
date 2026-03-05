import os
from dotenv import load_dotenv

load_dotenv()

def _fix_db_url(url: str) -> str:
    """Railway injects postgres:// but SQLAlchemy requires postgresql://"""
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url

class Settings:
    DATABASE_URL: str = _fix_db_url(
        os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/triple_i")
    )
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")

    AZURE_OPENAI_API_KEY: str = os.getenv("AZURE_OPENAI_API_KEY", "")
    AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    AZURE_OPENAI_DEPLOYMENT: str = os.getenv("AZURE_OPENAI_DEPLOYMENT", "")
    AZURE_OPENAI_API_VERSION: str = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")

    COST_PER_INPUT_TOKEN: float = float(os.getenv("COST_PER_INPUT_TOKEN", "0.000005"))
    COST_PER_OUTPUT_TOKEN: float = float(os.getenv("COST_PER_OUTPUT_TOKEN", "0.000015"))

    # LinkedIn API
    LINKEDIN_ACCESS_TOKEN: str = os.getenv("LINKEDIN_ACCESS_TOKEN", "")
    LINKEDIN_PERSON_ID: str = os.getenv("LINKEDIN_PERSON_ID", "")
    LINKEDIN_ORG_ID: str = os.getenv("LINKEDIN_ORG_ID", "")

settings = Settings()
