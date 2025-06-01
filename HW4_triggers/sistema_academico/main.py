from src.services.analytics_service import AnalyticsService

def main():
    service = AnalyticsService()

    df = service.ver_rendimiento_estudiantes()
    print(df)

    df2 = service.ver_promedio_por_materia()
    print(df2)

    service.exportar_a_csv(df2, "promedios.csv")

if __name__ == "__main__":
    main()