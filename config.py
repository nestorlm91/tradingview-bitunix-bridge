from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    BITUNIX_API_KEY = os.getenv("BITUNIX_API_KEY")
    BITUNIX_SECRET_KEY = os.getenv("BITUNIX_SECRET_KEY")
    SECURITY_TOKEN = os.getenv("SECURITY_TOKEN", "SECRETO123")

settings = Settings()
