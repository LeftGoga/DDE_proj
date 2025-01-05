from dotenv import load_dotenv
import os
load_dotenv("../.env")
print(os.getenv("DB_PATH"))
print(type(os.getenv("DB_PATH")))