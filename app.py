import psycopg2
import os

DATABASE_URL = os.getenv("DATABASE_URL")

try:
    conn = psycopg2.connect(DATABASE_URL)
    print("Connection successful!")
    conn.close()
except psycopg2.Error as e:
    print(f"Connection failed: {e}")

print("Script finished.")