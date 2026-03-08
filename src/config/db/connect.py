import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def obtener_conexion():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "student_match"),
        user=os.getenv("DB_USER", "user"),
        password=os.getenv("DB_PASS", "password"),
        port=os.getenv("DB_PORT", "5432")
    )