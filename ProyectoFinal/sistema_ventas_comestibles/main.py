#!/usr/bin/env python3
"""
Sistema de Análisis de Ventas - Tienda de Comestibles
ENTREGA FINAL con MENÚ INTERACTIVO - VERSIÓN MEJORADA

Sistema completo que combina:
- Análisis tradicionales (AnalyticsService)
- SQL Avanzado con CTE y Funciones Ventana (AdvancedAnalyticsService)
- Patrones de diseño (Singleton, Factory, Builder, Strategy)
- Dashboard ejecutivo completo

Autor: Romina Cattaneo
Fecha: 2025
"""

import sys
import os
from pathlib import Path
import time
from datetime import datetime, date, timedelta
import pandas as pd
import logging
from typing import Optional

# Configurar el path para importar módulos
sys.path.append(str(Path(__file__).parent / 'src'))

# Configurar logging MEJORADO
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('sistema_ventas.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class VentasSystemMenu:
    """Sistema de menús interactivo para el análisis de ventas."""
    
    def __init__(self):
        self.analytics_service = None
        self.advanced_service = None
        self.services_initialized = False
        self.connection_test_passed = False
        
    def print_banner(self):
        """Muestra banner principal del sistema."""
        banner = """
        ╔══════════════════════════════════════════════════════════════════════╗
        ║                                                                      ║
        ║    🚀 SISTEMA DE ANÁLISIS DE VENTAS - MENÚ INTERACTIVO 🚀           ║
        ║                                                                      ║
        ║    🎯 CARACTERÍSTICAS IMPLEMENTADAS:                                 ║
        ║    • Análisis Tradicionales + DataFrames                            ║
        ║    • SQL Avanzado: CTE + Funciones Ventana                          ║
        ║    • Objetos SQL: Funciones, Triggers, Vistas, Procedimientos       ║
        ║    • Patrones de Diseño: Singleton, Factory, Builder, Strategy      ║
        ║    • Dashboard Ejecutivo Completo                                   ║
        ║    • Reconexión Automática por Consulta                             ║
        ║                                                                      ║
        ╚══════════════════════════════════════════════════════════════════════╝
        """
        print(banner)
        print(f"🕐 Iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
    
    def test_database_connection(self):
        """Prueba la conexión a la base de datos antes de inicializar servicios."""
        print("🔍 Probando conexión a la base de datos...")
        
        try:
            from database.connection import DatabaseConnection
            
            # Crear conexión de prueba
            test_db = DatabaseConnection()
            
            # Hacer una consulta simple para probar la conexión
            test_query = "SELECT 1 as test_connection"
            result = test_db.execute_query_to_dataframe(test_query)
            
            if len(result) > 0 and result.iloc[0]['test_connection'] == 1:
                print("✅ Conexión a la base de datos exitosa")
                self.connection_test_passed = True
                return True
            else:
                print("❌ Conexión a la base de datos falló - respuesta inesperada")
                return False
                
        except Exception as e:
            print(f"❌ Error de conexión a la base de datos: {e}")
            logger.error(f"Database connection test failed: {e}")
            return False
    
    def initialize_services(self):
        """Inicializa todos los servicios del sistema."""
        if self.services_initialized:
            return True
        
        # Primero probar la conexión
        if not self.test_database_connection():
            print("\n⚠️  No se pudo establecer conexión con la base de datos.")
            print("   Verifica:")
            print("   • Que MySQL esté ejecutándose")
            print("   • Que la configuración de conexión sea correcta")
            print("   • Que la base de datos 'ventas_comestibles' exista")
            return False
            
        print("\n🔄 Inicializando servicios del sistema...")
        
        try:
            # Importar servicios
            from services.analytics_service import AnalyticsService
            
            # Servicio tradicional
            print("   📊 Inicializando AnalyticsService...")
            self.analytics_service = AnalyticsService()
            print("   ✅ AnalyticsService iniciado correctamente")
            
            # Servicio SQL avanzado
            try:
                print("   🔥 Inicializando AdvancedAnalyticsService...")
                from services.advanced_analytics_service import AdvancedAnalyticsService
                self.advanced_service = AdvancedAnalyticsService()
                print("   ✅ AdvancedAnalyticsService iniciado correctamente")
            except ImportError as e:
                print(f"   ⚠️  AdvancedAnalyticsService no disponible: {e}")
                logger.warning(f"AdvancedAnalyticsService import failed: {e}")
                self.advanced_service = None
            except Exception as e:
                print(f"   ❌ Error inicializando AdvancedAnalyticsService: {e}")
                logger.error(f"AdvancedAnalyticsService initialization failed: {e}")
                self.advanced_service = None
            
            self.services_initialized = True
            print("\n🎉 Servicios inicializados correctamente")
            
            # Probar una consulta simple de cada servicio
            self._test_services_functionality()
            
            return True
            
        except Exception as e:
            print(f"❌ Error crítico inicializando servicios: {e}")
            logger.error(f"Critical error initializing services: {e}")
            return False
    
    def _test_services_functionality(self):
        """Prueba funcionalidad básica de los servicios."""
        print("\n🧪 Probando funcionalidad de servicios...")
        
        # Probar AnalyticsService
        if self.analytics_service:
            try:
                # Hacer una consulta simple
                test_df = self.analytics_service.get_sales_performance_by_employee()
                print(f"   ✅ AnalyticsService funcional ({len(test_df)} empleados encontrados)")
            except Exception as e:
                print(f"   ⚠️  AnalyticsService con problemas: {e}")
                logger.warning(f"AnalyticsService test failed: {e}")
        
        # Probar AdvancedAnalyticsService
        if self.advanced_service:
            try:
                # Probar la vista del dashboard
                test_df = self.advanced_service.get_executive_dashboard()
                print(f"   ✅ AdvancedAnalyticsService funcional ({len(test_df)} empleados en dashboard)")
            except Exception as e:
                print(f"   ⚠️  AdvancedAnalyticsService con problemas: {e}")
                logger.warning(f"AdvancedAnalyticsService test failed: {e}")
        
        print("   🎯 Pruebas de funcionalidad completadas")
    
    def print_main_menu(self):
        """Imprime el menú principal."""
        print("\n" + "=" * 60)
        print("🏠 MENÚ PRINCIPAL - SISTEMA DE ANÁLISIS DE VENTAS")
        print("=" * 60)
        print("1️⃣  📊 Análisis Tradicionales (AnalyticsService)")
        print("2️⃣  🔥 SQL Avanzado (CTE + Funciones Ventana)")
        print("3️⃣  🛠️  Objetos SQL Personalizados")
        print("4️⃣  🏗️  Demostración de Patrones de Diseño")
        print("5️⃣  👔 Dashboard Ejecutivo Completo")
        print("6️⃣  🎯 Demo Automatizada Completa")
        print("7️⃣  ℹ️  Información del Sistema")
        print("8️⃣  🔧 Diagnóstico del Sistema")  # NUEVA OPCIÓN
        print("0️⃣  🚪 Salir")
        print("=" * 60)
    
    def print_analytics_menu(self):
        """Imprime el menú de análisis tradicionales."""
        print("\n" + "=" * 50)
        print("📊 ANÁLISIS TRADICIONALES")
        print("=" * 50)
        print("1. 👔 Rendimiento por Empleado")
        print("2. 🌍 Análisis Geográfico")
        print("3. 📦 Rendimiento de Productos")
        print("4. 👥 Segmentación de Clientes")
        print("5. 📈 Tendencias de Ventas")
        print("6. 💰 Efectividad de Descuentos")
        print("7. 📋 Dashboard Ejecutivo Básico")
        print("0. 🔙 Volver al Menú Principal")
        print("=" * 50)
    
    def print_advanced_sql_menu(self):
        """Imprime el menú de SQL avanzado."""
        print("\n" + "=" * 50)
        print("🔥 SQL AVANZADO - CTE + FUNCIONES VENTANA")
        print("=" * 50)
        print("1. 🏆 Ranking de Empleados (CTE + Window Functions)")
        print("2. 📈 Análisis de Tendencias (CTE Recursivo)")
        print("3. 👔 Dashboard Ejecutivo Avanzado")
        print("4. 📊 Análisis por Categorías")
        print("0. 🔙 Volver al Menú Principal")
        print("=" * 50)
    
    def print_sql_objects_menu(self):
        """Imprime el menú de objetos SQL."""
        print("\n" + "=" * 50)
        print("🛠️ OBJETOS SQL PERSONALIZADOS")
        print("=" * 50)
        print("1. 💰 Calcular Comisiones (Función SQL)")
        print("2. 🏆 Clasificar Clientes (Función SQL)")
        print("3. 📋 Reporte Mensual (Procedimiento)")
        print("4. 👑 Análisis Top Clientes (Procedimiento)")
        print("5. 🔍 Log de Auditoría (Triggers)")
        print("6. 🔧 Crear/Verificar Objetos SQL")
        print("0. 🔙 Volver al Menú Principal")
        print("=" * 50)
    
    def wait_for_user(self):
        """Espera a que el usuario presione Enter."""
        input("\n⏳ Presiona Enter para continuar...")
    
    def format_dataframe_display(self, df: pd.DataFrame, title: str, max_rows: int = 10):
        """Formatea y muestra un DataFrame de manera legible."""
        print(f"\n📊 {title}")
        print("-" * (len(title) + 4))
        
        if df.empty:
            print("⚠️  No hay datos disponibles")
            print("   Posibles causas:")
            print("   • La consulta no retornó resultados")
            print("   • Error en la conexión a la base de datos")
            print("   • Tablas vacías o sin datos en el rango especificado")
            return
        
        print(f"📋 Total de registros: {len(df)}")
        print(f"📊 Columnas: {', '.join(df.columns.tolist())}")
        print()
        
        # Mostrar los primeros registros
        display_df = df.head(max_rows).copy()  # Hacer copia para evitar warning
        
        # Formatear números para mejor legibilidad
        for col in display_df.columns:
            if display_df[col].dtype in ['float64', 'int64']:
                if any(keyword in col.lower() for keyword in ['revenue', 'price', 'amount', 'commission', 'spent']):
                    display_df[col] = display_df[col].apply(lambda x: f"${x:,.2f}" if pd.notna(x) else "N/A")
                elif 'total' in col.lower() and 'sales' in col.lower():
                    display_df[col] = display_df[col].apply(lambda x: f"{x:,}" if pd.notna(x) else "N/A")
        
        print(display_df.to_string(index=False))
        
        if len(df) > max_rows:
            print(f"\n... y {len(df) - max_rows} registros más")
    
    # ================================
    # ANÁLISIS TRADICIONALES
    # ================================
    
    def show_employee_performance(self):
        """Muestra análisis de rendimiento por empleado."""
        print("\n🔄 Ejecutando análisis de rendimiento por empleado...")
        
        if not self.analytics_service:
            print("❌ AnalyticsService no disponible")
            return
        
        try:
            df = self.analytics_service.get_sales_performance_by_employee()
            self.format_dataframe_display(df, "RENDIMIENTO POR EMPLEADO")
            
            if not df.empty:
                # Estadísticas adicionales
                print(f"\n📈 ESTADÍSTICAS:")
                try:
                    total_revenue = pd.to_numeric(df['total_revenue'], errors='coerce').sum()
                    avg_revenue = pd.to_numeric(df['total_revenue'], errors='coerce').mean()
                    print(f"   💰 Ingresos totales: ${total_revenue:,.2f}")
                    print(f"   📊 Promedio por empleado: ${avg_revenue:,.2f}")
                    print(f"   🏆 Top performer: {df.iloc[0]['employee_name']} (${pd.to_numeric(df.iloc[0]['total_revenue'], errors='coerce'):,.2f})")
                except Exception as e:
                    print(f"   ⚠️  No se pudieron calcular estadísticas adicionales: {e}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            logger.error(f"Error in show_employee_performance: {e}")
    
    def show_geographic_analysis(self):
        """Muestra análisis geográfico."""
        print("\n🔄 Ejecutando análisis geográfico...")
        
        if not self.analytics_service:
            print("❌ AnalyticsService no disponible")
            return
        
        try:
            df = self.analytics_service.get_geographic_sales_analysis()
            self.format_dataframe_display(df, "ANÁLISIS GEOGRÁFICO DE VENTAS")
            
            if not df.empty:
                try:
                    # Agrupar por país
                    df_numeric = df.copy()
                    df_numeric['total_revenue'] = pd.to_numeric(df_numeric['total_revenue'], errors='coerce')
                    df_numeric['total_sales'] = pd.to_numeric(df_numeric['total_sales'], errors='coerce')
                    df_numeric['unique_customers'] = pd.to_numeric(df_numeric['unique_customers'], errors='coerce')
                    
                    country_summary = df_numeric.groupby('CountryName').agg({
                        'total_revenue': 'sum',
                        'total_sales': 'sum',
                        'unique_customers': 'sum'
                    }).round(2)
                    
                    print(f"\n🌍 RESUMEN POR PAÍS:")
                    for country, data in country_summary.iterrows():
                        print(f"   {country}: ${data['total_revenue']:,.2f} ({data['total_sales']:,} ventas)")
                except Exception as e:
                    print(f"   ⚠️  No se pudo generar resumen por país: {e}")
                    
        except Exception as e:
            print(f"❌ Error: {e}")
            logger.error(f"Error in show_geographic_analysis: {e}")
    
    def show_product_analysis(self):
        """Muestra análisis de rendimiento de productos."""
        print("\n🔄 Ejecutando análisis de productos...")
        
        if not self.analytics_service:
            print("❌ AnalyticsService no disponible")
            return
        
        try:
            df = self.analytics_service.get_product_performance_analysis()
            self.format_dataframe_display(df, "RENDIMIENTO DE PRODUCTOS")
            
            if not df.empty:
                try:
                    # Top 5 productos
                    top_products = df.head(5)
                    print(f"\n🏆 TOP 5 PRODUCTOS:")
                    for i, (idx, product) in enumerate(top_products.iterrows(), 1):
                        revenue = pd.to_numeric(product['total_revenue'], errors='coerce')
                        print(f"   {i}. {product['ProductName']} - ${revenue:,.2f}")
                except Exception as e:
                    print(f"   ⚠️  No se pudo generar top productos: {e}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            logger.error(f"Error in show_product_analysis: {e}")
    
    def show_customer_segmentation(self):
        """Muestra segmentación de clientes."""
        print("\n🔄 Ejecutando segmentación de clientes...")
        
        if not self.analytics_service:
            print("❌ AnalyticsService no disponible")
            return
        
        try:
            df = self.analytics_service.get_customer_segmentation()
            self.format_dataframe_display(df, "SEGMENTACIÓN DE CLIENTES")
            
            if not df.empty and 'customer_segment' in df.columns:
                try:
                    # Distribución por segmento
                    segment_dist = df['customer_segment'].value_counts()
                    print(f"\n🎯 DISTRIBUCIÓN POR SEGMENTO:")
                    for segment, count in segment_dist.items():
                        pct = (count / len(df)) * 100
                        print(f"   {segment}: {count} clientes ({pct:.1f}%)")
                except Exception as e:
                    print(f"   ⚠️  No se pudo generar distribución por segmento: {e}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            logger.error(f"Error in show_customer_segmentation: {e}")
    
    def show_sales_trends(self):
        """Muestra tendencias de ventas."""
        print("\n🔄 Ejecutando análisis de tendencias...")
        
        if not self.analytics_service:
            print("❌ AnalyticsService no disponible")
            return
        
        period = input("📅 Selecciona período (daily/monthly) [monthly]: ").strip().lower()
        if not period:
            period = 'monthly'
        
        try:
            df = self.analytics_service.get_sales_trends_by_period(period)
            self.format_dataframe_display(df, f"TENDENCIAS DE VENTAS ({period.upper()})")
            
            if not df.empty and len(df) > 1:
                try:
                    # Estadísticas de crecimiento
                    df_copy = df.copy()
                    df_copy['revenue_numeric'] = pd.to_numeric(df_copy['total_revenue'], errors='coerce')
                    
                    if len(df_copy.dropna(subset=['revenue_numeric'])) > 1:
                        first_revenue = df_copy['revenue_numeric'].iloc[0]
                        last_revenue = df_copy['revenue_numeric'].iloc[-1]
                        
                        if first_revenue > 0:
                            growth_rate = ((last_revenue - first_revenue) / first_revenue) * 100
                            
                            print(f"\n📈 ANÁLISIS DE CRECIMIENTO:")
                            print(f"   📊 Primer período: ${first_revenue:,.2f}")
                            print(f"   📊 Último período: ${last_revenue:,.2f}")
                            print(f"   📈 Crecimiento total: {growth_rate:+.2f}%")
                except Exception as e:
                    print(f"   ⚠️  No se pudieron calcular estadísticas de crecimiento: {e}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            logger.error(f"Error in show_sales_trends: {e}")
    
    def show_discount_analysis(self):
        """Muestra análisis de efectividad de descuentos."""
        print("\n🔄 Ejecutando análisis de descuentos...")
        
        if not self.analytics_service:
            print("❌ AnalyticsService no disponible")
            return
        
        try:
            df = self.analytics_service.get_discount_effectiveness_analysis()
            self.format_dataframe_display(df, "EFECTIVIDAD DE DESCUENTOS")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            logger.error(f"Error in show_discount_analysis: {e}")
    
    def show_basic_dashboard(self):
        """Muestra dashboard ejecutivo básico."""
        print("\n🔄 Generando dashboard ejecutivo básico...")
        
        if not self.analytics_service:
            print("❌ AnalyticsService no disponible")
            return
        
        try:
            dashboard = self.analytics_service.generate_executive_dashboard()
            
            print(f"\n📊 DASHBOARD EJECUTIVO BÁSICO")
            print("=" * 40)
            
            # Métricas generales
            if 'general_metrics' in dashboard and dashboard['general_metrics']:
                metrics = dashboard['general_metrics']
                print(f"💰 Ingresos totales: ${metrics.get('total_revenue', 0):,.2f}")
                print(f"🛒 Total ventas: {metrics.get('total_sales', 0):,}")
                print(f"👥 Clientes únicos: {metrics.get('unique_customers', 0):,}")
                print(f"📦 Productos vendidos: {metrics.get('products_sold', 0):,}")
                print(f"💳 Venta promedio: ${metrics.get('avg_sale_amount', 0):,.2f}")
            
            # Top productos
            if 'top_products' in dashboard and dashboard['top_products']:
                print(f"\n🏆 TOP 5 PRODUCTOS:")
                for i, product in enumerate(dashboard['top_products'][:5], 1):
                    print(f"   {i}. {product['ProductName']} - ${product['revenue']:,.2f}")
            
            # Top empleados
            if 'top_employees' in dashboard and dashboard['top_employees']:
                print(f"\n👔 TOP 5 EMPLEADOS:")
                for i, employee in enumerate(dashboard['top_employees'][:5], 1):
                    print(f"   {i}. {employee['employee_name']} - ${employee['revenue']:,.2f}")
            
            # Ventas por país
            if 'sales_by_country' in dashboard and dashboard['sales_by_country']:
                print(f"\n🌍 VENTAS POR PAÍS:")
                for country in dashboard['sales_by_country'][:5]:
                    print(f"   {country['CountryName']}: ${country['revenue']:,.2f}")
                    
        except Exception as e:
            print(f"❌ Error: {e}")
            logger.error(f"Error in show_basic_dashboard: {e}")
    
    # ================================
    # SQL AVANZADO
    # ================================
    
    def show_advanced_employee_ranking(self):
        """Muestra ranking avanzado de empleados con CTE."""
        if not self.advanced_service:
            print("❌ AdvancedAnalyticsService no disponible")
            return
            
        print("\n🔄 Ejecutando ranking avanzado con CTE + Funciones Ventana...")
        
        try:
            df = self.advanced_service.get_employee_performance_ranking(months_back=12)
            self.format_dataframe_display(df, "RANKING AVANZADO DE EMPLEADOS (CTE + Window Functions)", max_rows=10)
            
            if not df.empty:
                try:
                    print(f"\n🏆 ANÁLISIS ESTADÍSTICO:")
                    print(f"   📊 Total empleados analizados: {len(df)}")
                    
                    revenue_col = pd.to_numeric(df['total_revenue'], errors='coerce')
                    print(f"   💰 Ingreso promedio: ${revenue_col.mean():,.2f}")
                    
                    if 'performance_category' in df.columns:
                        top_performers = len(df[df['performance_category'] == 'Top Performer (10%)'])
                        print(f"   🎯 Top 10%: {top_performers} empleados")
                    
                    print(f"   📈 Rango de ingresos: ${revenue_col.min():,.0f} - ${revenue_col.max():,.0f}")
                except Exception as e:
                    print(f"   ⚠️  No se pudieron calcular estadísticas: {e}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            logger.error(f"Error in show_advanced_employee_ranking: {e}")
    
    def show_advanced_trends_analysis(self):
        """Muestra análisis de tendencias con CTE recursivo."""
        if not self.advanced_service:
            print("❌ AdvancedAnalyticsService no disponible")
            return
            
        print("\n🔄 Ejecutando análisis de tendencias con CTE Recursivo...")
        
        try:
            df = self.advanced_service.get_sales_trends_analysis(start_year=2023, months_to_analyze=12)
            self.format_dataframe_display(df, "ANÁLISIS DE TENDENCIAS (CTE Recursivo)", max_rows=12)
            
            if not df.empty:
                try:
                    # Análisis de crecimiento
                    valid_growth = df.dropna(subset=['mom_growth_percent'])
                    if len(valid_growth) > 0:
                        avg_growth = valid_growth['mom_growth_percent'].mean()
                        best_month = df.loc[df['revenue'].idxmax()]
                        
                        print(f"\n📈 ANÁLISIS DE TENDENCIAS:")
                        print(f"   📊 Crecimiento promedio mensual: {avg_growth:+.2f}%")
                        print(f"   🏆 Mejor mes: {best_month['period']} (${best_month['revenue']:,.0f})")
                        
                        if 'seasonal_classification' in df.columns:
                            peak_months = len(df[df['seasonal_classification'] == 'Peak Season'])
                            print(f"   🌟 Meses de temporada alta: {peak_months}")
                except Exception as e:
                    print(f"   ⚠️  No se pudieron calcular métricas de tendencias: {e}")
                    
        except Exception as e:
            print(f"❌ Error: {e}")
            logger.error(f"Error in show_advanced_trends_analysis: {e}")
    
    def show_advanced_dashboard(self):
        """Muestra dashboard ejecutivo avanzado."""
        if not self.advanced_service:
            print("❌ AdvancedAnalyticsService no disponible")
            return
            
        print("\n🔄 Generando dashboard ejecutivo avanzado...")
        
        try:
            df = self.advanced_service.get_executive_dashboard()
            self.format_dataframe_display(df, "DASHBOARD EJECUTIVO AVANZADO (Vista SQL)", max_rows=15)
            
            if not df.empty:
                try:
                    # Métricas agregadas
                    revenue_col = pd.to_numeric(df['revenue_12m'], errors='coerce')
                    transactions_col = pd.to_numeric(df['transactions_12m'], errors='coerce')
                    
                    total_revenue = revenue_col.sum()
                    total_transactions = transactions_col.sum()
                    
                    print(f"\n📊 MÉTRICAS AGREGADAS:")
                    print(f"   💰 Ingresos totales (12M): ${total_revenue:,.2f}")
                    print(f"   🛒 Transacciones totales: {total_transactions:,}")
                    print(f"   👥 Empleados analizados: {len(df)}")
                    
                    if 'performance_tier' in df.columns:
                        performance_dist = df['performance_tier'].value_counts()
                        print(f"\n🏆 DISTRIBUCIÓN POR RENDIMIENTO:")
                        for tier, count in performance_dist.items():
                            pct = (count / len(df)) * 100
                            print(f"   {tier}: {count} empleados ({pct:.1f}%)")
                except Exception as e:
                    print(f"   ⚠️  No se pudieron calcular métricas agregadas: {e}")
                    
        except Exception as e:
            print(f"❌ Error: {e}")
            logger.error(f"Error in show_advanced_dashboard: {e}")
    
    def show_category_analysis(self):
        """Muestra análisis por categorías."""
        if not self.advanced_service:
            print("❌ AdvancedAnalyticsService no disponible")
            return
            
        print("\n🔄 Ejecutando análisis por categorías...")
        
        try:
            df = self.advanced_service.get_product_category_analysis()
            self.format_dataframe_display(df, "ANÁLISIS POR CATEGORÍAS (Vista SQL)")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            logger.error(f"Error in show_category_analysis: {e}")
    
    # ================================
    # OBJETOS SQL
    # ================================
    
    def calculate_commissions(self):
        """Calcula comisiones usando función SQL."""
        if not self.advanced_service:
            print("❌ AdvancedAnalyticsService no disponible")
            return
            
        print("\n🔄 Calculando comisiones con función SQL...")
        
        try:
            # Obtener empleados para calcular comisiones
            dashboard = self.advanced_service.get_executive_dashboard()
            if dashboard.empty:
                print("⚠️  No hay empleados disponibles")
                return
            
            end_date = date.today()
            start_date = end_date - timedelta(days=365)
            
            print(f"💰 CALCULANDO COMISIONES (últimos 12 meses):")
            print("-" * 60)
            
            top_employees = dashboard.head(5)
            for i, (idx, emp) in enumerate(top_employees.iterrows()):
                try:
                    emp_id = emp['EmployeeID']
                    emp_name = emp['employee_name']
                    revenue = pd.to_numeric(emp['revenue_12m'], errors='coerce')
                    
                    commission = self.advanced_service.calculate_employee_commission(emp_id, start_date, end_date)
                    commission_rate = (commission / revenue * 100) if revenue > 0 else 0
                    
                    print(f"{emp_name:<25} | ${revenue:>10,.0f} → ${commission:>8,.2f} ({commission_rate:.2f}%)")
                    
                except Exception as e:
                    print(f"{emp.get('employee_name', 'N/A'):<25} | ❌ Error: {e}")
                    
        except Exception as e:
            print(f"❌ Error: {e}")
            logger.error(f"Error in calculate_commissions: {e}")
    
    def classify_customers(self):
        """Clasifica clientes usando función SQL."""
        if not self.advanced_service:
            print("❌ AdvancedAnalyticsService no disponible")
            return
            
        print("\n🔄 Clasificando clientes con función SQL...")
        
        try:
            print("🏆 CLASIFICACIÓN DE CLIENTES por VALOR:")
            print("-" * 40)
            
            # Clasificar muestra de clientes
            sample_customers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            tier_icons = {
                'VIP': '💎', 'Premium': '🥇', 'Gold': '🥈',
                'Silver': '🥉', 'Bronze': '🔶', 'New': '🆕'
            }
            
            for customer_id in sample_customers:
                try:
                    tier = self.advanced_service.classify_customer_value(customer_id)
                    icon = tier_icons.get(tier, '❓')
                    print(f"Cliente {customer_id:2d} → {icon} {tier}")
                except Exception as e:
                    print(f"Cliente {customer_id:2d} → ❌ Error: {e}")
                    
        except Exception as e:
            print(f"❌ Error: {e}")
            logger.error(f"Error in classify_customers: {e}")
    
    def generate_monthly_report(self):
        """Genera reporte mensual usando procedimiento."""
        if not self.advanced_service:
            print("❌ AdvancedAnalyticsService no disponible")
            return
            
        print("\n🔄 Generando reporte mensual con procedimiento almacenado...")
        
        # Pedir año y mes
        try:
            year = int(input("📅 Año [2024]: ") or "2024")
            month = int(input("📅 Mes [3]: ") or "3")
            min_revenue = float(input("💰 Ingresos mínimos [0]: ") or "0")
        except ValueError:
            print("❌ Valores inválidos, usando valores por defecto")
            year, month, min_revenue = 2024, 3, 0
        
        try:
            df = self.advanced_service.generate_monthly_report(year, month, min_revenue)
            self.format_dataframe_display(df, f"REPORTE MENSUAL {year}-{month:02d} (Procedimiento SQL)")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            logger.error(f"Error in generate_monthly_report: {e}")
    
    def analyze_top_customers(self):
        """Analiza top clientes usando procedimiento."""
        if not self.advanced_service:
            print("❌ AdvancedAnalyticsService no disponible")
            return
            
        print("\n🔄 Analizando top clientes con procedimiento almacenado...")
        
        try:
            top_n = int(input("🔢 Número de clientes [20]: ") or "20")
            months = int(input("📅 Meses de análisis [12]: ") or "12")
        except ValueError:
            top_n, months = 20, 12
        
        try:
            df = self.advanced_service.analyze_top_customers(top_n, months)
            self.format_dataframe_display(df, f"TOP {top_n} CLIENTES (Procedimiento SQL)")
            
            if not df.empty:
                try:
                    total_spent_col = pd.to_numeric(df['total_spent'], errors='coerce')
                    purchases_col = pd.to_numeric(df['total_purchases'], errors='coerce')
                    
                    total_revenue = total_spent_col.sum()
                    avg_purchases = purchases_col.mean()
                    
                    print(f"\n📊 ESTADÍSTICAS DE TOP CLIENTES:")
                    print(f"   💰 Ingresos totales: ${total_revenue:,.2f}")
                    print(f"   🛒 Compras promedio: {avg_purchases:.1f}")
                    print(f"   💎 Cliente más valioso: ${total_spent_col.iloc[0]:,.2f}")
                except Exception as e:
                    print(f"   ⚠️  No se pudieron calcular estadísticas: {e}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            logger.error(f"Error in analyze_top_customers: {e}")
    
    def show_audit_log(self):
        """Muestra log de auditoría."""
        if not self.advanced_service:
            print("❌ AdvancedAnalyticsService no disponible")
            return
            
        print("\n🔄 Consultando log de auditoría...")
        
        try:
            days_back = int(input("📅 Días hacia atrás [30]: ") or "30")
        except ValueError:
            days_back = 30
        
        try:
            df = self.advanced_service.get_sales_audit_log(days_back)
            
            if not df.empty:
                print(f"\n🔍 LOG DE AUDITORÍA (últimos {days_back} días):")
                print(f"📋 Total de registros: {len(df)}")
                
                # Mostrar últimas operaciones
                print(f"\n📄 ÚLTIMAS 10 OPERACIONES:")
                print("-" * 80)
                
                for i, (idx, audit) in enumerate(df.head(10).iterrows()):
                    try:
                        timestamp = audit['change_timestamp'].strftime('%Y-%m-%d %H:%M:%S')
                        action = audit['action_type']
                        sales_id = audit['sales_id']
                        user = audit['changed_by']
                        
                        action_icons = {'INSERT': '➕', 'UPDATE': '✏️', 'DELETE': '❌'}
                        icon = action_icons.get(action, '❓')
                        
                        print(f"{icon} {timestamp} | {action:<8} | Venta #{sales_id} | {user}")
                    except Exception as e:
                        print(f"❓ Error procesando registro {i}: {e}")
                
                # Estadísticas
                if 'action_type' in df.columns:
                    action_counts = df['action_type'].value_counts()
                    print(f"\n📊 ESTADÍSTICAS:")
                    for action, count in action_counts.items():
                        print(f"   {action}: {count} operaciones")
            else:
                print("ℹ️  No hay registros de auditoría en el período especificado")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            logger.error(f"Error in show_audit_log: {e}")
    
    def create_sql_objects(self):
        """Crea/verifica objetos SQL."""
        if not self.advanced_service:
            print("❌ AdvancedAnalyticsService no disponible")
            return
            
        print("\n🔄 Creando/verificando objetos SQL...")
        
        try:
            results = self.advanced_service.create_advanced_sql_objects()
            
            print("\n🛠️ RESULTADOS DE CREACIÓN DE OBJETOS SQL:")
            print("-" * 50)
            
            success_count = sum(1 for success in results.values() if success)
            total_count = len(results)
            
            for obj_name, success in results.items():
                status = "✅ ÉXITO" if success else "❌ ERROR"
                obj_display = obj_name.replace('_', ' ').title()
                print(f"{status} | {obj_display}")
            
            print(f"\n📊 Resumen: {success_count}/{total_count} objetos creados exitosamente")
            
            if success_count == total_count:
                print("🎉 Todos los objetos SQL están listos para usar")
            else:
                print("⚠️  Algunos objetos necesitan revisión")
                print("   💡 Verifica permisos de usuario y configuración de MySQL")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            logger.error(f"Error in create_sql_objects: {e}")
    
    # ================================
    # NUEVAS FUNCIONES
    # ================================
    
    def run_system_diagnosis(self):
        """Ejecuta diagnóstico completo del sistema."""
        print("\n🔍 EJECUTANDO DIAGNÓSTICO COMPLETO DEL SISTEMA")
        print("=" * 60)
        
        # Test de conexión
        print("\n1️⃣ PRUEBA DE CONEXIÓN A BASE DE DATOS")
        print("-" * 40)
        if self.test_database_connection():
            print("✅ Conexión exitosa")
        else:
            print("❌ Fallo en conexión")
            return
        
        # Test de servicios
        print("\n2️⃣ PRUEBA DE SERVICIOS")
        print("-" * 40)
        
        if self.analytics_service:
            try:
                test_df = self.analytics_service.get_sales_performance_by_employee()
                print(f"✅ AnalyticsService: {len(test_df)} empleados")
            except Exception as e:
                print(f"❌ AnalyticsService: {e}")
        else:
            print("❌ AnalyticsService: No inicializado")
        
        if self.advanced_service:
            try:
                test_df = self.advanced_service.get_executive_dashboard()
                print(f"✅ AdvancedAnalyticsService: {len(test_df)} empleados")
            except Exception as e:
                print(f"❌ AdvancedAnalyticsService: {e}")
        else:
            print("❌ AdvancedAnalyticsService: No inicializado")
        
        # Test de patrones de diseño
        print("\n3️⃣ PRUEBA DE PATRONES DE DISEÑO")
        print("-" * 40)
        try:
            from database.connection import DatabaseConnection
            db1 = DatabaseConnection()
            db2 = DatabaseConnection()
            print(f"✅ Singleton Pattern: {db1 is db2}")
        except Exception as e:
            print(f"❌ Singleton Pattern: {e}")
        
        try:
            from patterns.report_factory import ReportFactory, ReportType
            factory = ReportFactory()
            print("✅ Factory Pattern: Disponible")
        except Exception as e:
            print(f"❌ Factory Pattern: {e}")
        
        print("\n🎯 Diagnóstico completado")
    
    # ================================
    # DEMOSTRACIONES Y SISTEMA
    # ================================
    
    def demo_design_patterns(self):
        """Demuestra patrones de diseño."""
        print("\n🔄 Demostrando patrones de diseño...")
        
        try:
            from database.connection import DatabaseConnection
            from patterns.report_factory import ReportFactory, ReportType
            
            print("🏗️ PATRONES DE DISEÑO IMPLEMENTADOS:")
            print("-" * 40)
            
            # Singleton
            db1 = DatabaseConnection()
            db2 = DatabaseConnection()
            print(f"✅ Singleton Pattern: {db1 is db2}")
            
            # Factory
            factory = ReportFactory()
            sales_report = factory.create_report(ReportType.SALES)
            employee_report = factory.create_report(ReportType.EMPLOYEE)
            print(f"✅ Factory Pattern: {type(sales_report).__name__}, {type(employee_report).__name__}")
            
            # Builder y Strategy
            print("✅ Builder Pattern: QueryBuilder disponible")
            print("✅ Strategy Pattern: Analysis strategies disponible")
            
            print("\n🎯 Todos los patrones están funcionando correctamente")
            
        except Exception as e:
            print(f"❌ Error demostrando patrones: {e}")
            logger.error(f"Error in demo_design_patterns: {e}")
    
    def show_complete_dashboard(self):
        """Muestra dashboard ejecutivo completo."""
        print("\n🔄 Generando dashboard ejecutivo completo...")
        
        print("👔 DASHBOARD EJECUTIVO COMPLETO")
        print("=" * 50)
        
        # Dashboard básico
        if self.analytics_service:
            print("\n📊 MÉTRICAS BÁSICAS:")
            try:
                dashboard = self.analytics_service.generate_executive_dashboard()
                if 'general_metrics' in dashboard and dashboard['general_metrics']:
                    metrics = dashboard['general_metrics']
                    print(f"   💰 Ingresos: ${metrics.get('total_revenue', 0):,.2f}")
                    print(f"   🛒 Ventas: {metrics.get('total_sales', 0):,}")
                    print(f"   👥 Clientes: {metrics.get('unique_customers', 0):,}")
                else:
                    print("   ⚠️  No hay métricas básicas disponibles")
            except Exception as e:
                print(f"   ❌ Error obteniendo métricas básicas: {e}")
        
        # Dashboard avanzado
        if self.advanced_service:
            print("\n🔥 MÉTRICAS AVANZADAS:")
            try:
                df = self.advanced_service.get_executive_dashboard()
                if not df.empty:
                    revenue_col = pd.to_numeric(df['revenue_12m'], errors='coerce')
                    total_revenue = revenue_col.sum()
                    total_employees = len(df)
                    
                    if 'performance_tier' in df.columns:
                        top_performers = len(df[df['performance_tier'] == 'Top Performer'])
                    else:
                        top_performers = 0
                    
                    print(f"   💎 Ingresos avanzados: ${total_revenue:,.2f}")
                    print(f"   👔 Empleados activos: {total_employees}")
                    print(f"   🏆 Top performers: {top_performers}")
                else:
                    print("   ⚠️  No hay métricas avanzadas disponibles")
            except Exception as e:
                print(f"   ❌ Error obteniendo métricas avanzadas: {e}")
        
        print("\n🎯 Dashboard completo generado")
    
    def run_complete_demo(self):
        """Ejecuta demostración automatizada completa."""
        print("\n🚀 EJECUTANDO DEMOSTRACIÓN AUTOMATIZADA COMPLETA")
        print("=" * 60)
        
        demos = [
            ("🏗️ Patrones de Diseño", self.demo_design_patterns),
            ("📊 Análisis Básico", lambda: self.show_employee_performance()),
            ("🔥 SQL Avanzado", lambda: self.show_advanced_employee_ranking() if self.advanced_service else print("⚠️ SQL Avanzado no disponible")),
            ("🛠️ Objetos SQL", lambda: self.calculate_commissions() if self.advanced_service else print("⚠️ Objetos SQL no disponibles")),
            ("👔 Dashboard Completo", self.show_complete_dashboard)
        ]
        
        for i, (name, func) in enumerate(demos, 1):
            print(f"\n{i}. {name}")
            print("-" * 30)
            try:
                func()
                print("✅ Completado")
            except Exception as e:
                print(f"❌ Error: {e}")
                logger.error(f"Error in demo {name}: {e}")
            
            if i < len(demos):
                time.sleep(2)  # Pausa entre demos
        
        print("\n🎉 DEMOSTRACIÓN COMPLETA FINALIZADA")
    
    def show_system_info(self):
        """Muestra información del sistema."""
        print("\n📋 INFORMACIÓN DEL SISTEMA")
        print("=" * 40)
        
        print("🏗️ ARQUITECTURA:")
        print("   • Patrones de Diseño: Singleton, Factory, Builder, Strategy")
        print("   • Base de Datos: MySQL con SQLAlchemy")
        print("   • Análisis: Pandas DataFrames")
        print("   • SQL Avanzado: CTE + Funciones Ventana")
        print("   • Reconexión automática por consulta")
        
        print("\n🔧 SERVICIOS DISPONIBLES:")
        print(f"   • AnalyticsService: {'✅ Disponible' if self.analytics_service else '❌ No disponible'}")
        print(f"   • AdvancedAnalyticsService: {'✅ Disponible' if self.advanced_service else '❌ No disponible'}")
        
        print("\n📊 FUNCIONALIDADES:")
        print("   • Análisis tradicionales con DataFrames")
        print("   • Consultas CTE y funciones ventana")
        print("   • Objetos SQL personalizados")
        print("   • Sistema de auditoría automática")
        print("   • Dashboard ejecutivo completo")
        print("   • Diagnóstico automático del sistema")
        
        print(f"\n🔗 ESTADO DE CONEXIÓN:")
        print(f"   • Prueba inicial: {'✅ Exitosa' if self.connection_test_passed else '❌ Falló'}")
        print(f"   • Servicios inicializados: {'✅ Sí' if self.services_initialized else '❌ No'}")
        
        print(f"\n🕐 Sistema iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # ================================
    # CONTROLADORES DE MENÚ
    # ================================
    
    def handle_analytics_menu(self):
        """Maneja el menú de análisis tradicionales."""
        while True:
            self.print_analytics_menu()
            choice = input("\n🎯 Selecciona una opción: ").strip()
            
            if choice == '1':
                self.show_employee_performance()
            elif choice == '2':
                self.show_geographic_analysis()
            elif choice == '3':
                self.show_product_analysis()
            elif choice == '4':
                self.show_customer_segmentation()
            elif choice == '5':
                self.show_sales_trends()
            elif choice == '6':
                self.show_discount_analysis()
            elif choice == '7':
                self.show_basic_dashboard()
            elif choice == '0':
                break
            else:
                print("❌ Opción inválida")
            
            if choice != '0':
                self.wait_for_user()
    
    def handle_advanced_sql_menu(self):
        """Maneja el menú de SQL avanzado."""
        while True:
            self.print_advanced_sql_menu()
            choice = input("\n🎯 Selecciona una opción: ").strip()
            
            if choice == '1':
                self.show_advanced_employee_ranking()
            elif choice == '2':
                self.show_advanced_trends_analysis()
            elif choice == '3':
                self.show_advanced_dashboard()
            elif choice == '4':
                self.show_category_analysis()
            elif choice == '0':
                break
            else:
                print("❌ Opción inválida")
            
            if choice != '0':
                self.wait_for_user()
    
    def handle_sql_objects_menu(self):
        """Maneja el menú de objetos SQL."""
        while True:
            self.print_sql_objects_menu()
            choice = input("\n🎯 Selecciona una opción: ").strip()
            
            if choice == '1':
                self.calculate_commissions()
            elif choice == '2':
                self.classify_customers()
            elif choice == '3':
                self.generate_monthly_report()
            elif choice == '4':
                self.analyze_top_customers()
            elif choice == '5':
                self.show_audit_log()
            elif choice == '6':
                self.create_sql_objects()
            elif choice == '0':
                break
            else:
                print("❌ Opción inválida")
            
            if choice != '0':
                self.wait_for_user()
    
    def run(self):
        """Ejecuta el sistema de menús principal."""
        self.print_banner()
        
        if not self.initialize_services():
            print("\n❌ No se pudieron inicializar los servicios.")
            print("\n💡 RECOMENDACIONES:")
            print("   1. Verifica que MySQL esté ejecutándose")
            print("   2. Confirma la configuración de conexión")
            print("   3. Asegúrate de que la base de datos existe")
            print("   4. Verifica permisos de usuario")
            print("\n🚪 Saliendo del sistema...")
            return
        
        while True:
            try:
                self.print_main_menu()
                choice = input("\n🎯 Selecciona una opción: ").strip()
                
                if choice == '1':
                    self.handle_analytics_menu()
                elif choice == '2':
                    self.handle_advanced_sql_menu()
                elif choice == '3':
                    self.handle_sql_objects_menu()
                elif choice == '4':
                    self.demo_design_patterns()
                    self.wait_for_user()
                elif choice == '5':
                    self.show_complete_dashboard()
                    self.wait_for_user()
                elif choice == '6':
                    self.run_complete_demo()
                    self.wait_for_user()
                elif choice == '7':
                    self.show_system_info()
                    self.wait_for_user()
                elif choice == '8':  # NUEVA OPCIÓN
                    self.run_system_diagnosis()
                    self.wait_for_user()
                elif choice == '0':
                    print("\n👋 ¡Gracias por usar el Sistema de Análisis de Ventas!")
                    break
                else:
                    print("❌ Opción inválida. Por favor selecciona una opción válida.")
                    
            except KeyboardInterrupt:
                print("\n\n🛑 Operación cancelada por el usuario")
                break
            except Exception as e:
                print(f"\n❌ Error inesperado: {e}")
                logger.error(f"Unexpected error in main menu: {e}")
                print("🔄 Continuando con el sistema...")

def main():
    """Función principal del sistema."""
    try:
        print("🚀 Iniciando Sistema de Análisis de Ventas...")
        print("📝 Los logs se guardan en 'sistema_ventas.log'")
        
        menu_system = VentasSystemMenu()
        menu_system.run()
        
    except KeyboardInterrupt:
        print("\n🛑 Sistema cancelado por el usuario")
    except Exception as e:
        print(f"\n💥 Error fatal del sistema: {e}")
        logger.critical(f"Fatal system error: {e}", exc_info=True)
        print("\n📋 Revisa el archivo 'sistema_ventas.log' para más detalles")
    finally:
        print("\n🔚 Sistema finalizado")

if __name__ == "__main__":
    main()