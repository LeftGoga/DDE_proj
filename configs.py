from dotenv import load_dotenv
import os
load_dotenv(".env")
DB_PATH = os.getenv("DB_PATH")