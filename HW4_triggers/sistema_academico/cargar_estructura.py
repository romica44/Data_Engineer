from sqlalchemy import create_engine, text
from src.database.connection import DatabaseConnection
from dotenv import load_dotenv
import os

def crear_base_de_datos():
    load_dotenv()
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", 3306)
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "")

    engine = create_engine(f"mysql+mysqlconnector://{user}:{password}@{host}:{port}")

    with engine.connect() as conn:
        conn.execute(text("CREATE DATABASE IF NOT EXISTS sistema_academico"))
        print("✅ Base de datos creada o ya existente.")

    engine.dispose()

def ejecutar_sql_script(path: str, engine):
    with open(path, "r", encoding="utf-8") as f:
        script = f.read()

    # Separar por "DELIMITER $$" y ejecutar bloques
    for bloque in script.split("DELIMITER $$"):
        for stmt in bloque.strip().split("$$"):
            if stmt.strip():
                with engine.begin() as conn:
                    conn.execute(text(stmt.strip()))

if __name__ == "__main__":
    crear_base_de_datos()

    db = DatabaseConnection()
    db.connect()

    ejecutar_sql_script("sistema_academico.sql", db._engine)
    print("✅ Script SQL ejecutado correctamente.")