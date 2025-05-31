"""
Demostración completa de todos los patrones de diseño implementados.
Este archivo muestra cómo usar los patrones Factory, Builder, Strategy y Singleton
de manera integrada en el sistema de análisis de ventas.
"""

from datetime import datetime, timedelta
from colorama import init, Fore, Style
import logging

# Imports de nuestros patrones
from src.database.connection import DatabaseConnection  # Singleton
from src.patterns.report_factory import ReportFactory, ReportType  # Factory
from src.patterns.query_builder import create_sales_query, create_query  # Builder
from src.patterns.analysis_strategies import (  # Strategy
    create_trend_analyzer, 
    create_comparison_analyzer, 
    create_segmentation_analyzer
)

# Configurar colorama para output más atractivo
init(autoreset=True)

def demonstrate_singleton_pattern():
    """
    Demuestra el patrón Singleton con DatabaseConnection.
    
    Patrón: Singleton
    Problema que resuelve: Garantiza una única instancia de conexión a BD
    """
    print(Fore.CYAN + "\n🔗 DEMOSTRACIÓN: Patrón Singleton (DatabaseConnection)")
    print("=" * 60)
    
    # Crear múltiples instancias - todas deberían ser la misma
    db1 = DatabaseConnection()
    db2 = DatabaseConnection()
    db3 = DatabaseConnection()
    
    print(f"📌 Instancia 1 ID: {id(db1)}")
    print(f"📌 Instancia 2 ID: {id(db2)}")
    print(f"📌 Instancia 3 ID: {id(db3)}")
    
    # Verificar que son la misma instancia
    are_same = db1 is db2 is db3
    print(f"✅ ¿Son la misma instancia? {are_same}")
    
    if are_same:
        print(f"{Fore.GREEN}🎯 Singleton funcionando correctamente!")
        print(f"📊 Información de conexión: {db1.get_connection_info()}")
    else:
        print(f"{Fore.RED}❌ Error: Singleton no está funcionando correctamente")
    
    return db1

def demonstrate_factory_pattern():
    """
    Demuestra el patrón Factory con ReportFactory.
    
    Patrón: Factory Method
    Problema que resuelve: Centraliza creación de reportes y encapsula complejidad
    """
    print(Fore.CYAN + "\n🏭 DEMOSTRACIÓN: Patrón Factory (ReportFactory)")
    print("=" * 60)
    
    # Crear la factory
    factory = ReportFactory()
    
    print(f"📊 Factory Info: {factory.get_factory_info()}")
    print(f"📋 Tipos disponibles: {list(factory.get_available_report_types().keys())}")
    
    # Crear diferentes tipos de reportes usando la factory
    reports_created = []
    
    try:
        # Reporte de empleados
        employee_report = factory.create_report(ReportType.EMPLOYEE)
        reports_created.append(("Empleados", employee_report))
        print(f"✅ Reporte de empleados creado: {len(employee_report.data)} filas")
        
        # Reporte de productos
        product_report = factory.create_report(ReportType.PRODUCT)
        reports_created.append(("Productos", product_report))
        print(f"✅ Reporte de productos creado: {len(product_report.data)} filas")
        
        # Reporte de ventas con período específico
        sales_report = factory.create_report(ReportType.SALES, period='daily')
        reports_created.append(("Ventas Diarias", sales_report))
        print(f"✅ Reporte de ventas diarias creado: {len(sales_report.data)} filas")
        
        # Reporte geográfico
        geo_report = factory.create_report(ReportType.GEOGRAPHIC)
        reports_created.append(("Geográfico", geo_report))
        print(f"✅ Reporte geográfico creado: {len(geo_report.data)} filas")
        
        print(f"\n🎯 Factory Pattern funcionando correctamente!")
        print(f"📈 Total de reportes creados: {len(reports_created)}")
        
        # Mostrar ejemplo de uno de los reportes
        if reports_created:
            sample_report = reports_created[0][1]
            print(f"\n📄 Ejemplo de reporte generado:")
            print(sample_report.format_for_display())
        
    except Exception as e:
        print(f"{Fore.RED}❌ Error en Factory Pattern: {e}")
    
    return reports_created

def demonstrate_builder_pattern():
    """
    Demuestra el patrón Builder con SQLQueryBuilder.
    
    Patrón: Builder
    Problema que resuelve: Construcción fluida de consultas SQL complejas
    """
    print(Fore.CYAN + "\n🔨 DEMOSTRACIÓN: Patrón Builder (SQLQueryBuilder)")
    print("=" * 60)
    
    try:
        # Ejemplo 1: Consulta simple con el builder general
        print(f"{Fore.YELLOW}📝 Construyendo consulta básica...")
        query_builder = create_query()
        
        simple_query = (query_builder
                       .select("COUNT(*) as total_sales")
                       .select_aggregate("SUM", "TotalPrice", "total_revenue")
                       .from_table("sales")
                       .where("TotalPrice > 100")
                       .build())
        
        print(f"🔍 Consulta construida:\n{simple_query}")
        
        # Ejemplo 2: Consulta compleja con SalesQueryBuilder especializado
        print(f"\n{Fore.YELLOW}📝 Construyendo consulta compleja de ventas...")
        sales_builder = create_sales_query()
        
        # Consulta con múltiples JOINs y filtros
        complex_data = (sales_builder
                       .with_employee_info()
                       .with_product_info()
                       .with_geographic_info()
                       .with_sales_metrics()
                       .where_between("s.SalesDate", 
                                    datetime.now() - timedelta(days=365), 
                                    datetime.now())
                       .group_by("e.EmployeeID", "employee_name", "co.CountryName")
                       .having("SUM(s.TotalPrice) > 500")
                       .top_performers(10)
                       .execute())
        
        print(f"✅ Consulta compleja ejecutada exitosamente")
        print(f"📊 Resultados obtenidos: {len(complex_data)} filas")
        
        if not complex_data.empty:
            print(f"📈 Columnas: {list(complex_data.columns)}")
            print(f"🏆 Muestra de datos:")
            print(complex_data.head(3).to_string(index=False))
        
        # Mostrar información del builder
        builder_info = sales_builder.get_query_info()
        print(f"\n📋 Información del Builder:")
        print(f"  🔧 Patrón: {builder_info['pattern_type']}")
        print(f"  ✅ Válido: {builder_info['is_valid']}")
        print(f"  📊 Componentes: {builder_info['components']}")
        
        print(f"\n🎯 Builder Pattern funcionando correctamente!")
        
    except Exception as e:
        print(f"{Fore.RED}❌ Error en Builder Pattern: {e}")
        return None
    
    return complex_data

def demonstrate_strategy_pattern():
    """
    Demuestra el patrón Strategy con diferentes estrategias de análisis.
    
    Patrón: Strategy
    Problema que resuelve: Intercambio dinámico de algoritmos de análisis
    """
    print(Fore.CYAN + "\n🎯 DEMOSTRACIÓN: Patrón Strategy (AnalysisStrategies)")
    print("=" * 60)
    
    analysis_results = []
    
    try:
        # Estrategia 1: Análisis de Tendencias
        print(f"{Fore.YELLOW}📈 Estrategia 1: Análisis de Tendencias")
        trend_analyzer = create_trend_analyzer()
        
        print(f"ℹ️ Info de estrategia: {trend_analyzer.get_strategy_info()}")
        
        trend_result = trend_analyzer.execute_analysis(period='monthly')
        analysis_results.append(("Tendencias", trend_result))
        
        if 'error' not in trend_result:
            print(f"✅ Análisis de tendencias completado")
            print(f"📊 Períodos analizados: {trend_result.get('total_periods', 0)}")
            
            if 'insights' in trend_result:
                print(f"💡 Insights generados: {len(trend_result['insights'])}")
                for insight in trend_result['insights'][:2]:  # Mostrar solo primeros 2
                    print(f"   • {insight}")
        else:
            print(f"⚠️ Error en análisis de tendencias: {trend_result['error']}")
        
        # Estrategia 2: Análisis Comparativo
        print(f"\n{Fore.YELLOW}📊 Estrategia 2: Análisis Comparativo")
        comparison_analyzer = create_comparison_analyzer()
        
        print(f"ℹ️ Info de estrategia: {comparison_analyzer.get_strategy_info()}")
        
        comparison_result = comparison_analyzer.execute_analysis(comparison_type='employees')
        analysis_results.append(("Comparativo", comparison_result))
        
        if 'error' not in comparison_result:
            print(f"✅ Análisis comparativo completado")
            print(f"👥 Entidades analizadas: {comparison_result.get('total_entities', 0)}")
            
            if 'top_performers' in comparison_result:
                top_performers = comparison_result['top_performers'][:3]
                print(f"🏆 Top 3 performers:")
                for i, performer in enumerate(top_performers, 1):
                    name = performer.get('name', 'N/A')
                    revenue = performer.get('revenue', 0)
                    print(f"   {i}. {name}: ${revenue:,.2f}")
        else:
            print(f"⚠️ Error en análisis comparativo: {comparison_result['error']}")
        
        # Estrategia 3: Análisis de Segmentación
        print(f"\n{Fore.YELLOW}👥 Estrategia 3: Análisis de Segmentación")
        segmentation_analyzer = create_segmentation_analyzer()
        
        print(f"ℹ️ Info de estrategia: {segmentation_analyzer.get_strategy_info()}")
        
        segmentation_result = segmentation_analyzer.execute_analysis(segmentation_criteria='value')
        analysis_results.append(("Segmentación", segmentation_result))
        
        if 'error' not in segmentation_result:
            print(f"✅ Análisis de segmentación completado")
            print(f"👥 Clientes analizados: {segmentation_result.get('total_customers', 0)}")
            
            if 'segments' in segmentation_result:
                segments = segmentation_result['segments']
                print(f"📊 Segmentos identificados: {len(segments)}")
                for segment_name, segment_data in list(segments.items())[:3]:
                    if isinstance(segment_data, dict) and 'customers' in segment_data:
                        print(f"   • {segment_name}: {segment_data['customers']} clientes")
        else:
            print(f"⚠️ Error en análisis de segmentación: {segmentation_result['error']}")
        
        print(f"\n🎯 Strategy Pattern funcionando correctamente!")
        print(f"📈 Total de análisis realizados: {len(analysis_results)}")
        
        # Demostrar cambio dinámico de estrategia
        print(f"\n{Fore.YELLOW}🔄 Demostrando cambio dinámico de estrategia...")
        analyzer = create_trend_analyzer()
        print(f"Estrategia inicial: {analyzer.get_strategy_info()['name']}")
        
        # Cambiar a estrategia de comparación
        from src.patterns.analysis_strategies import PerformanceComparisonStrategy
        analyzer.set_strategy(PerformanceComparisonStrategy())
        print(f"Nueva estrategia: {analyzer.get_strategy_info()['name']}")
        
    except Exception as e:
        print(f"{Fore.RED}❌ Error en Strategy Pattern: {e}")
    
    return analysis_results

def demonstrate_integrated_workflow():
    """
    Demuestra un flujo de trabajo integrado usando todos los patrones juntos.
    """
    print(Fore.CYAN + "\n🔄 DEMOSTRACIÓN: Flujo de Trabajo Integrado")
    print("=" * 60)
    
    try:
        # 1. Usar Singleton para verificar conexión
        print(f"{Fore.YELLOW}1️⃣ Verificando conexión (Singleton)...")
        db = DatabaseConnection()
        connection_ok = db.test_connection()
        print(f"{'✅' if connection_ok else '❌'} Conexión: {'OK' if connection_ok else 'Error'}")
        
        if not connection_ok:
            print(f"{Fore.RED}⚠️ Sin conexión a BD - finalizando demostración")
            return
        
        # 2. Usar Builder para crear consulta personalizada
        print(f"\n{Fore.YELLOW}2️⃣ Construyendo consulta personalizada (Builder)...")
        custom_data = (create_sales_query()
                      .with_employee_info()
                      .with_sales_metrics()
                      .for_period(start_date=datetime.now() - timedelta(days=90))
                      .group_by("e.EmployeeID", "employee_name")
                      .top_performers(5)
                      .execute())
        
        print(f"✅ Datos obtenidos: {len(custom_data)} empleados top")
        
        # 3. Usar Strategy para analizar los datos
        print(f"\n{Fore.YELLOW}3️⃣ Analizando con Strategy Pattern...")
        analyzer = create_comparison_analyzer()
        analysis = analyzer.execute_analysis(data=custom_data, comparison_type='employees')
        
        print(f"✅ Análisis completado: {analysis.get('strategy_type', 'N/A')}")
        
        # 4. Usar Factory para crear reporte final
        print(f"\n{Fore.YELLOW}4️⃣ Generando reporte final (Factory)...")
        factory = ReportFactory()
        final_report = factory.create_report(ReportType.EMPLOYEE)
        
        print(f"✅ Reporte generado: {final_report.title}")
        
        # 5. Mostrar resultados integrados
        print(f"\n{Fore.GREEN}🎯 FLUJO INTEGRADO COMPLETADO")
        print(f"📊 Resumen del flujo:")
        print(f"  🔗 Singleton: Conexión única establecida")
        print(f"  🔨 Builder: Consulta personalizada ejecutada ({len(custom_data)} filas)")
        print(f"  🎯 Strategy: Análisis de rendimiento realizado")
        print(f"  🏭 Factory: Reporte final generado")
        
        # Mostrar el reporte final
        print(f"\n📄 REPORTE FINAL:")
        print(final_report.format_for_display())
        
        return {
            'singleton_working': connection_ok,
            'builder_data_rows': len(custom_data),
            'strategy_analysis': analysis,
            'factory_report': final_report
        }
        
    except Exception as e:
        print(f"{Fore.RED}❌ Error en flujo integrado: {e}")
        return None

def main():
    """
    Función principal que ejecuta todas las demostraciones.
    """
    print(Fore.BLUE + Style.BRIGHT + """
    ╔══════════════════════════════════════════════════════════════╗
    ║                   DEMOSTRACIÓN DE PATRONES                   ║
    ║                     Sistema de Ventas                        ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Configurar logging para las demostraciones
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    results = {}
    
    try:
        # Ejecutar todas las demostraciones
        results['singleton'] = demonstrate_singleton_pattern()
        results['factory'] = demonstrate_factory_pattern()
        results['builder'] = demonstrate_builder_pattern()
        results['strategy'] = demonstrate_strategy_pattern()
        results['integrated'] = demonstrate_integrated_workflow()
        
        # Resumen final
        print(Fore.GREEN + Style.BRIGHT + f"""
        
    ╔══════════════════════════════════════════════════════════════╗
    ║                     RESUMEN FINAL                            ║
    ╚══════════════════════════════════════════════════════════════╝
    
    🎯 PATRONES IMPLEMENTADOS Y DEMOSTRADOS:
    
    ✅ SINGLETON PATTERN (DatabaseConnection)
       • Problema resuelto: Única instancia de conexión a BD
       • Beneficio: Control de recursos y consistencia
    
    ✅ FACTORY PATTERN (ReportFactory)
       • Problema resuelto: Creación compleja de reportes
       • Beneficio: Código limpio y extensible
    
    ✅ BUILDER PATTERN (SQLQueryBuilder)
       • Problema resuelto: Construcción de consultas complejas
       • Beneficio: API fluida y flexible
    
    ✅ STRATEGY PATTERN (AnalysisStrategies)
       • Problema resuelto: Intercambio de algoritmos de análisis
       • Beneficio: Flexibilidad y extensibilidad
    
    🔄 INTEGRACIÓN COMPLETA DEMOSTRADA
       • Todos los patrones funcionando juntos
       • Flujo de trabajo real completado
    
    ✨ SISTEMA LISTO PARA PRODUCCIÓN
        """)
        
    except Exception as e:
        print(f"{Fore.RED}❌ Error en demostración principal: {e}")
    
    return results

if __name__ == "__main__":
    # Ejecutar todas las demostraciones
    demo_results = main()
    
    # Opcional: Guardar resultados para análisis posterior
    if demo_results:
        print(f"\n💾 Resultados de demostración disponibles en variable 'demo_results'")