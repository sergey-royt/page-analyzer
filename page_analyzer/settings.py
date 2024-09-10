from dotenv import load_dotenv
import os


load_dotenv()

# Postgres data base url
DATABASE_URL = os.getenv("DATABASE_URL")

SECRET_KEY = os.getenv("SECRET_KEY")
# minimum quantity of opened connections in connections pool
MINCONN = os.getenv("MINCONN", 2)
# maximum quantity of opened connections in connections pool
MAXCONN = os.getenv("MAXCONN", 3)
