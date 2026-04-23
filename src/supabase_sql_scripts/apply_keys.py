import os
import psycopg2
from dotenv import load_dotenv

load_dotenv("../../.env")
db_url = os.getenv("DATABASE_URL")

if not db_url:
    print("❌ DIDN'T FIND DATABASE URL.")
    exit(1)

try:
    print("🚀 CONNECTING TO SUPABASE..")
    conn = psycopg2.connect(db_url)
    conn.autocommit = True 
    cursor = conn.cursor()


    sql_path = "keys.sql"
    with open(sql_path, "r", encoding="utf-8") as file:
        sql_script = file.read()


    print(f"📦 RUNNING -> {sql_path}...")
    cursor.execute(sql_script)

    print("✅ ¡KEYS APPLIED IN SUPABASE!")

except Exception as e:
    print(f"❌ SOMETHING WENT WRONG!: {e}")
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()
