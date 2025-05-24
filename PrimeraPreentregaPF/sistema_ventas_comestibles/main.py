from colorama import init, Fore, Style
from src.services.analytics_service import AnalyticsService

init(autoreset=True)  # Para que el color se reinicie automáticamente después de cada print

def main():
    analytics = AnalyticsService()

    print(Fore.CYAN + "\n🔷 Dashboard Ejecutivo")
    dashboard = analytics.generate_executive_dashboard()
    print(f"{Fore.YELLOW}Total Ventas:{Style.RESET_ALL} {dashboard['general_metrics']['total_sales']}")
    print(f"{Fore.YELLOW}Total Ingresos:{Style.RESET_ALL} ${dashboard['general_metrics']['total_revenue']:.2f}")

    print(Fore.CYAN + "\n🏆 Top Productos")
    for p in dashboard['top_products']:
        print(f" - {Fore.GREEN}{p['ProductName']}{Style.RESET_ALL}: ${p['revenue']:.2f}")

    print(Fore.CYAN + "\n👔 Top Empleados")
    for e in dashboard['top_employees']:
        print(f" - {Fore.MAGENTA}{e['employee_name']}{Style.RESET_ALL}: ${e['revenue']:.2f}")

    print(Fore.CYAN + "\n🌎 Ventas por País")
    for c in dashboard['sales_by_country']:
        print(f" - {Fore.BLUE}{c['CountryName']}{Style.RESET_ALL}: ${c['revenue']:.2f}")

    print(Fore.CYAN + "\n📊 Ventas por Empleado")
    for r in analytics.get_sales_performance_by_employee():
        print(f"{r['employee_name']}: {r['total_sales']} ventas - ${r['total_revenue']:.2f}")

    print(Fore.CYAN + "\n📍 Análisis Geográfico de Ventas")
    for r in analytics.get_geographic_sales_analysis():
        print(f"{r['CountryName']} - {r['CityName']}: ${r['total_revenue']:.2f}")

    print(Fore.CYAN + "\n📦 Rendimiento de Productos")
    for r in analytics.get_product_performance_analysis()[:5]:
        print(f"{r['ProductName']} ({r['CategoryName']}): {r['total_units_sold']} uds - ${r['total_revenue']:.2f}")

    print(Fore.CYAN + "\n👥 Segmentación de Clientes")
    for r in analytics.get_customer_segmentation()[:5]:
        print(f"{r['customer_name']} ({r['customer_segment']}): ${r['total_spent']:.2f}")

    print(Fore.CYAN + "\n📅 Tendencias Diarias de Venta")
    for r in analytics.get_sales_trends_by_period('daily')[-7:]:  # Últimos 7 días
        print(f"{r['period']}: ${r['total_revenue']:.2f}")

    print(Fore.CYAN + "\n💸 Análisis de Descuentos")
    for r in analytics.get_discount_effectiveness_analysis():
        print(f"{r['discount_range']}: {r['total_sales']} ventas - ${r['total_revenue']:.2f}")

if __name__ == "__main__":
    main()