import os
from dotenv import load_dotenv

# .env fájl betöltése
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("HIBA: A GEMINI_API_KEY nincs beállítva a .env fájlban!")