"""
Sistema de Reportes de Ventas con Soporte CSV
Implementa patrones Factory, Strategy, Decorator
"""

# ============================================================================
# IMPORTACIONES
# ============================================================================
import csv
import json
import logging
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from services import SalesReportingService
from config import Config
from data import datos_ventas


# ============================================================================
# CLASE CSVHandler - Manejo de archivos CSV
# ============================================================================
class CSVHandler:
    """Manejador especializado para archivos CSV de ventas"""
    
    REQUIRED_COLUMNS = ['categoria', 'producto', 'precio', 'cantidad', 'medio_venta', 'vendedor']
    
    def __init__(self, encoding='utf-8'):
        self.encoding = encoding
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Configurar logger para el manejador CSV"""
        logger = logging.getLogger('CSVHandler')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def read_csv(self, file_path: str, validate: bool = True) -> List[Dict[str, Any]]:
        """
        Leer archivo CSV y convertir a lista de diccionarios
        
        Args:
            file_path: Ruta al archivo CSV
            validate: Si validar los datos después de leer
            
        Returns:
            Lista de diccionarios con los datos de ventas
        """
        try:
            # Verificar si el archivo existe
            if not Path(file_path).exists():
                raise FileNotFoundError(f"El archivo {file_path} no existe")
            
            print(f"📂 Leyendo archivo CSV: {file_path}")
            
            # Leer CSV con pandas
            df = pd.read_csv(file_path, encoding=self.encoding)
            
            # Limpiar datos
            df = self._clean_dataframe(df)
            
            # Validar si se solicita
            if validate:
                self._validate_dataframe(df)
            
            # Convertir a lista de diccionarios
            data = df.to_dict('records')
            
            print(f"✅ CSV leído exitosamente: {len(data)} registros")
            return data
            
        except Exception as e:
            print(f"❌ Error al leer CSV: {str(e)}")
            raise
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Limpiar y preparar DataFrame"""
        # Limpiar nombres de columnas
        df.columns = df.columns.str.strip().str.lower()
        
        # Mapear nombres de columnas comunes
        column_mapping = {
            'categoría': 'categoria',
            'category': 'categoria',
            'price': 'precio',
            'quantity': 'cantidad',
            'sales_channel': 'medio_venta',
            'channel': 'medio_venta',
            'seller': 'vendedor',
        }
        
        df = df.rename(columns=column_mapping)
        
        # Limpiar datos de texto
        text_columns = ['categoria', 'producto', 'medio_venta', 'vendedor']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip().str.title()
        
        # Convertir tipos numéricos
        if 'precio' in df.columns:
            df['precio'] = pd.to_numeric(df['precio'], errors='coerce')
        
        if 'cantidad' in df.columns:
            df['cantidad'] = pd.to_numeric(df['cantidad'], errors='coerce')
        
        # Eliminar filas con datos críticos faltantes
        df = df.dropna(subset=['precio', 'cantidad'])
        
        return df
    
    def _validate_dataframe(self, df: pd.DataFrame) -> None:
        """Validar estructura y contenido del DataFrame"""
        # Verificar columnas requeridas
        missing_columns = set(self.REQUIRED_COLUMNS) - set(df.columns)
        if missing_columns:
            print(f"⚠️ Columnas faltantes: {missing_columns}")
        
        # Verificar que no esté vacío
        if df.empty:
            raise ValueError("El archivo CSV está vacío")
        
        # Validar rangos de valores
        if (df['precio'] <= 0).any():
            print("⚠️ Advertencia: Existen precios menores o iguales a cero")
        
        if (df['cantidad'] <= 0).any():
            print("⚠️ Advertencia: Existen cantidades menores o iguales a cero")
        
        print("✅ Validación de datos completada")
    
    def export_to_csv(self, data: List[Dict[str, Any]], file_path: str = None, 
                     include_totals: bool = True) -> str:
        """
        Exportar datos a archivo CSV
        
        Args:
            data: Lista de diccionarios con datos
            file_path: Ruta donde guardar el archivo
            include_totals: Si incluir fila de totales
            
        Returns:
            Ruta del archivo creado
        """
        try:
            if not file_path:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                file_path = f"datos_ventas_{timestamp}.csv"
            
            df = pd.DataFrame(data)
            
            # Agregar fila de totales si se solicita
            if include_totals and 'precio' in df.columns and 'cantidad' in df.columns:
                df['total_venta'] = df['precio'] * df['cantidad']
                
                # Crear fila de totales
                totals_row = {
                    'categoria': 'TOTAL',
                    'producto': '-',
                    'precio': df['precio'].mean(),
                    'cantidad': df['cantidad'].sum(),
                    'total_venta': df['total_venta'].sum(),
                    'medio_venta': '-',
                    'vendedor': '-'
                }
                
                df = pd.concat([df, pd.DataFrame([totals_row])], ignore_index=True)
            
            # Guardar a CSV
            df.to_csv(file_path, index=False, encoding=self.encoding)
            
            print(f"📁 Datos exportados a CSV: {file_path}")
            return file_path
            
        except Exception as e:
            print(f"❌ Error al exportar CSV: {str(e)}")
            raise
    
    def create_sample_csv(self, file_path: str = "sample_sales.csv") -> str:
        """Crear archivo CSV de muestra para testing"""
        sample_data = [
            {"categoria": "Electrónicos", "producto": "Laptop", "precio": 1200, "cantidad": 1, "medio_venta": "Web", "vendedor": "Ana Pérez"},
            {"categoria": "Libros", "producto": "Novela", "precio": 25, "cantidad": 2, "medio_venta": "Físico", "vendedor": "Carlos López"},
            {"categoria": "Electrónicos", "producto": "Smartphone", "precio": 800, "cantidad": 1, "medio_venta": "Web", "vendedor": "Ana Pérez"},
            {"categoria": "Ropa", "producto": "Camiseta", "precio": 30, "cantidad": 3, "medio_venta": "Físico", "vendedor": "Sofía Gómez"},
            {"categoria": "Libros", "producto": "Ciencia Ficción", "precio": 20, "cantidad": 1, "medio_venta": "Web", "vendedor": "Carlos López"}
        ]
        
        return self.export_to_csv(sample_data, file_path, include_totals=False)
    
    def analyze_csv_structure(self, file_path: str) -> Dict[str, Any]:
        """Analizar estructura de un archivo CSV"""
        try:
            # Leer primeras filas para análisis
            df_sample = pd.read_csv(file_path, nrows=5, encoding=self.encoding)
            
            # Contar total de filas
            with open(file_path, 'r', encoding=self.encoding) as f:
                total_rows = sum(1 for _ in f) - 1  # -1 por header
            
            analysis = {
                'nombre_archivo': Path(file_path).name,
                'total_filas': total_rows,
                'total_columnas': len(df_sample.columns),
                'columnas': df_sample.columns.tolist(),
                'primeras_filas': df_sample.to_dict('records'),
                'columnas_requeridas_presentes': set(self.REQUIRED_COLUMNS).issubset(set(df_sample.columns.str.lower())),
                'columnas_faltantes': list(set(self.REQUIRED_COLUMNS) - set(df_sample.columns.str.lower())),
                'tamaño_archivo_kb': f"{Path(file_path).stat().st_size / 1024:.2f}"
            }
            
            return analysis
            
        except Exception as e:
            print(f"❌ Error al analizar CSV: {str(e)}")
            raise


# ============================================================================
# CLASE CSVSalesReportingService - Servicio con soporte CSV
# ============================================================================
class CSVSalesReportingService(SalesReportingService):
    """Servicio de reportes con soporte nativo para CSV"""
    
    def __init__(self, csv_file: Optional[str] = None):
        self.csv_handler = CSVHandler()
        
        # Cargar datos desde CSV si se proporciona
        if csv_file:
            data = self.load_from_csv(csv_file)
        else:
            # Usar datos por defecto
            data = datos_ventas
        
        super().__init__(data)
        self.csv_file_path = csv_file
    
    def load_from_csv(self, file_path: str, validate: bool = True) -> List[Dict[str, Any]]:
        """Cargar datos desde archivo CSV"""
        try:
            data = self.csv_handler.read_csv(file_path, validate)
            self.data = data
            self.df = pd.DataFrame(data)
            self.csv_file_path = file_path
            
            print(f"✅ Datos cargados desde CSV: {len(data)} registros")
            return data
            
        except Exception as e:
            print(f"❌ Error al cargar CSV: {str(e)}")
            raise
    
    def export_raw_data_to_csv(self, file_path: str = None) -> str:
        """Exportar datos originales a CSV"""
        if not file_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_path = f"datos_ventas_{timestamp}.csv"
        
        return self.csv_handler.export_to_csv(self.data, file_path)
    
    def analyze_csv_file(self, file_path: str = None) -> str:
        """Analizar estructura del archivo CSV cargado"""
        target_file = file_path or self.csv_file_path
        
        if not target_file:
            return "❌ No hay archivo CSV cargado para analizar"
        
        try:
            analysis = self.csv_handler.analyze_csv_structure(target_file)
            
            output = []
            output.append(f"📊 ANÁLISIS DE ARCHIVO CSV")
            output.append("=" * 60)
            output.append(f"📄 Archivo: {analysis['nombre_archivo']}")
            output.append(f"📏 Dimensiones: {analysis['total_filas']} filas × {analysis['total_columnas']} columnas")
            output.append(f"💾 Tamaño: {analysis['tamaño_archivo_kb']} KB")
            output.append(f"✅ Estructura válida: {'Sí' if analysis['columnas_requeridas_presentes'] else 'No'}")
            
            if analysis['columnas_faltantes']:
                output.append(f"❌ Columnas faltantes: {', '.join(analysis['columnas_faltantes'])}")
            
            output.append("\n📋 COLUMNAS ENCONTRADAS:")
            for col in analysis['columnas']:
                output.append(f"   • {col}")
            
            output.append("\n🔍 PRIMERAS FILAS:")
            for i, row in enumerate(analysis['primeras_filas'], 1):
                output.append(f"   {i}. {row}")
            
            return "\n".join(output)
            
        except Exception as e:
            return f"❌ Error al analizar archivo: {str(e)}"


# ============================================================================
# CLASE SalesReportingSystem - Sistema principal con menú CSV
# ============================================================================
class SalesReportingSystem:
    """Sistema principal de reportes de ventas"""
    
    def __init__(self):
        self.service = SalesReportingService()
        self.csv_handler = CSVHandler()
    
    def run_interactive_mode(self):
        """Ejecutar modo interactivo con soporte CSV"""
        print(f"{Config.EMOJIS['rocket']} SISTEMA DE REPORTES DE VENTAS")
        print(Config.SEPARATOR_CHAR * Config.CONSOLE_WIDTH)
        
        while True:
            self._show_menu()
            choice = input("\nSelecciona una opción: ").strip()
            
            if choice == '1':
                self._show_data_summary()
            elif choice == '2':
                self._generate_specific_report()
            elif choice == '3':
                self._generate_all_reports()
            elif choice == '4':
                self._show_available_reports()
            elif choice == '5':
                self._load_csv_data()
            elif choice == '6':
                self._analyze_csv_file()
            elif choice == '7':
                self._create_sample_csv()
            elif choice == '8':
                self._export_data_to_csv()
            elif choice == '0':
                print(f"\n{Config.EMOJIS['success']} ¡Gracias por usar el sistema de reportes!")
                break
            else:
                print(f"\n{Config.EMOJIS['error']} Opción no válida. Intenta de nuevo.")
            
            input("\nPresiona Enter para continuar...")
    
    def _show_menu(self):
        """Mostrar menú principal con opciones CSV"""
        print(f"\n{Config.EMOJIS['report']} MENÚ PRINCIPAL")
        print("-" * 40)
        print("1. Ver resumen de datos")
        print("2. Generar reporte específico")
        print("3. Generar todos los reportes")
        print("4. Ver tipos de reportes disponibles")
        print("5. 📁 Cargar datos desde CSV")
        print("6. 📊 Analizar archivo CSV")
        print("7. 📄 Crear CSV de muestra")
        print("8. 💾 Exportar datos a CSV")
        print("0. Salir")
    
    def _show_data_summary(self):
        """Mostrar resumen de datos"""
        print("\n" + self.service.get_data_summary())
    
    def _generate_specific_report(self):
        """Generar reporte específico"""
        available_reports = self.service.get_available_reports()
        
        print(f"\n{Config.EMOJIS['search']} REPORTES DISPONIBLES:")
        for i, (key, name) in enumerate(available_reports.items(), 1):
            print(f"{i}. {name}")
        
        try:
            choice = int(input("\nSelecciona el número del reporte: "))
            report_keys = list(available_reports.keys())
            
            if 1 <= choice <= len(report_keys):
                report_type = report_keys[choice - 1]
                
                # Preguntar por formatos de exportación
                export_formats = self._get_export_formats()
                
                result = self.service.generate_report(report_type, export_formats)
                print("\n" + result)
            else:
                print(f"{Config.EMOJIS['error']} Número de reporte no válido.")
                
        except ValueError:
            print(f"{Config.EMOJIS['error']} Por favor ingresa un número válido.")
    
    def _generate_all_reports(self):
        """Generar todos los reportes"""
        export_formats = self._get_export_formats()
        
        print(f"\n{Config.EMOJIS['rocket']} GENERANDO TODOS LOS REPORTES...")
        print(Config.SEPARATOR_CHAR * Config.CONSOLE_WIDTH)
        
        results = self.service.generate_all_reports(export_formats)
        for result in results:
            print(result)
            print("\n")
    
    def _show_available_reports(self):
        """Mostrar tipos de reportes disponibles"""
        available_reports = self.service.get_available_reports()
        
        print(f"\n{Config.EMOJIS['report']} TIPOS DE REPORTES DISPONIBLES:")
        print("-" * 50)
        for key, name in available_reports.items():
            print(f"• {name} ({key})")
    
    def _load_csv_data(self):
        """Cargar datos desde archivo CSV"""
        file_path = input("📁 Ingresa la ruta del archivo CSV: ").strip()
        
        if not file_path:
            print("❌ Ruta de archivo requerida")
            return
        
        try:
            # Reemplazar el servicio actual con uno que carga CSV
            csv_service = CSVSalesReportingService(file_path)
            self.service = csv_service
            print("✅ Datos CSV cargados exitosamente")
            
            # Mostrar resumen automáticamente
            summary = self.service.get_data_summary()
            print(summary)
            
        except Exception as e:
            print(f"❌ Error al cargar CSV: {str(e)}")
    
    def _analyze_csv_file(self):
        """Analizar estructura de archivo CSV"""
        file_path = input("📊 Ingresa la ruta del archivo CSV a analizar: ").strip()
        
        if not file_path:
            print("❌ Ruta de archivo requerida")
            return
        
        try:
            analysis = self.csv_handler.analyze_csv_structure(file_path)
            
            # Mostrar análisis formateado
            print(f"\n📊 ANÁLISIS DE ARCHIVO CSV")
            print("=" * 60)
            print(f"📄 Archivo: {analysis['nombre_archivo']}")
            print(f"📏 Dimensiones: {analysis['total_filas']} filas × {analysis['total_columnas']} columnas")
            print(f"💾 Tamaño: {analysis['tamaño_archivo_kb']} KB")
            print(f"✅ Estructura válida: {'Sí' if analysis['columnas_requeridas_presentes'] else 'No'}")
            
            if analysis['columnas_faltantes']:
                print(f"❌ Columnas faltantes: {', '.join(analysis['columnas_faltantes'])}")
            
            print("\n📋 COLUMNAS ENCONTRADAS:")
            for col in analysis['columnas']:
                print(f"   • {col}")
                
        except Exception as e:
            print(f"❌ Error al analizar archivo: {str(e)}")
    
    def _create_sample_csv(self):
        """Crear archivo CSV de muestra"""
        filename = input("📄 Nombre del archivo (Enter para usar 'muestra_ventas.csv'): ").strip()
        if not filename:
            filename = "muestra_ventas.csv"
        
        try:
            created_file = self.csv_handler.create_sample_csv(filename)
            print(f"✅ Archivo CSV de muestra creado: {created_file}")
            
        except Exception as e:
            print(f"❌ Error al crear archivo: {str(e)}")
    
    def _export_data_to_csv(self):
        """Exportar datos actuales a CSV"""
        filename = input("💾 Nombre del archivo (Enter para auto-generar): ").strip()
        
        try:
            if hasattr(self.service, 'csv_handler'):
                # Si es CSVSalesReportingService
                result_file = self.service.export_raw_data_to_csv(filename if filename else None)
            else:
                # Si es SalesReportingService normal
                if not filename:
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"datos_exportados_{timestamp}.csv"
                result_file = self.csv_handler.export_to_csv(self.service.data, filename)
            
            print(f"✅ Datos exportados a: {result_file}")
            
        except Exception as e:
            print(f"❌ Error al exportar: {str(e)}")
    
    def _get_export_formats(self) -> list:
        """Obtener formatos de exportación del usuario"""
        print(f"\n{Config.EMOJIS['file']} ¿Deseas exportar los datos? (s/n): ", end="")
        if input().lower().startswith('s'):
            print("Formatos disponibles:", ", ".join(Config.SUPPORTED_EXPORT_FORMATS))
            formats_input = input("Ingresa los formatos separados por comas (o Enter para CSV): ").strip()
            
            if not formats_input:
                return ['csv']
            
            formats = [f.strip() for f in formats_input.split(',')]
            valid_formats = [f for f in formats if f in Config.SUPPORTED_EXPORT_FORMATS]
            
            if valid_formats:
                return valid_formats
            else:
                print(f"{Config.EMOJIS['error']} Formatos no válidos. Usando CSV por defecto.")
                return ['csv']
        
        return []
    
    def run_demo(self):
        """Ejecutar demostración completa"""
        print(f"{Config.EMOJIS['rocket']} DEMOSTRACIÓN DEL SISTEMA")
        print(Config.SEPARATOR_CHAR * Config.CONSOLE_WIDTH)
        
        # Mostrar resumen de datos
        print(self.service.get_data_summary())
        print("\n")
        
        # Generar todos los reportes con exportación
        results = self.service.generate_all_reports(['csv', 'excel', 'json'])
        for result in results:
            print(result)
            print("\n")


# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================
def main():
    """Función principal"""
    system = SalesReportingSystem()
    
    # Puedes elegir qué modo ejecutar:
    # system.run_demo()                    # Para demo automática
    system.run_interactive_mode()         # Para menú interactivo


if __name__ == "__main__":
    main()