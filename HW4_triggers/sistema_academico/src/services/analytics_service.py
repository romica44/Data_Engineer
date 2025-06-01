import logging
import pandas as pd
from src.database.connection import DatabaseConnection

class AnalyticsService:
    def __init__(self):
        self.db = DatabaseConnection()
        self.logger = logging.getLogger(__name__)

    def ver_rendimiento_estudiantes(self) -> pd.DataFrame:
        """
        Consulta la vista rendimiento_estudiantes
        """
        try:
            query = "SELECT * FROM rendimiento_estudiantes"
            return self.db.execute_query_to_dataframe(query)
        except Exception as e:
            self.logger.error(f"❌ Error al obtener rendimiento de estudiantes: {e}")
            return pd.DataFrame()

    def ver_promedio_por_materia(self) -> pd.DataFrame:
        """
        Consulta la vista promedio_materias
        """
        try:
            query = "SELECT * FROM promedio_materias"
            return self.db.execute_query_to_dataframe(query)
        except Exception as e:
            self.logger.error(f"❌ Error al obtener promedio por materia: {e}")
            return pd.DataFrame()

    def listar_calificaciones(self) -> pd.DataFrame:
        """
        Lista todas las calificaciones registradas
        """
        try:
            query = """
            SELECT e.nombre AS estudiante, m.nombre AS materia, c.nota, c.fecha
            FROM calificaciones c
            JOIN estudiantes e ON e.id = c.estudiante_id
            JOIN materias m ON m.id = c.materia_id
            ORDER BY c.fecha DESC
            """
            return self.db.execute_query_to_dataframe(query)
        except Exception as e:
            self.logger.error(f"❌ Error al listar calificaciones: {e}")
            return pd.DataFrame()

    def exportar_a_csv(self, df: pd.DataFrame, nombre: str):
        """
        Exporta cualquier DataFrame a CSV
        """
        try:
            if df.empty:
                print("⚠️ No hay datos para exportar.")
                return
            df.to_csv(nombre, index=False, encoding="utf-8")
            print(f"✅ Datos exportados en {nombre}")
        except Exception as e:
            print(f"❌ Error al exportar: {e}")