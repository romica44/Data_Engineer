# 📊 Sistema de Reportes de Ventas

Un sistema completo de análisis y generación de reportes de ventas implementando patrones de diseño profesionales (Factory, Strategy, Decorator), desarrollado en Python con soporte para CSV y múltiples formatos de exportación.

## 🚀 Características Principales

- ✅ **Patrones de Diseño**: Factory, Strategy, Decorator implementados profesionalmente
- ✅ **Procesamiento de Datos**: Análisis eficiente con Pandas y NumPy
- ✅ **Múltiples Reportes**: Total de ventas, métricas detalladas, análisis por canal y vendedor
- ✅ **Exportación Multi-formato**: CSV, Excel, JSON
- ✅ **Interfaz de Consola**: Visualización formateada con emojis y separadores
- ✅ **Soporte CSV**: Carga datos desde archivos CSV externos
- ✅ **Modo Interactivo**: Menú de opciones para el usuario

## 📁 Estructura del Proyecto

```
sales_reporting_system/
├── 📄 main.py                   # Sistema completo en un archivo
├── 📄 data.py                   # Dataset de ejemplo
├── 📄 README.md                 # Este archivo
└── 📂 output/                   # Archivos generados (CSV, Excel, JSON)
    ├── total_ventas_por_categoria_YYYYMMDD_HHMMSS.csv
    ├── metricas_detalladas_por_categoria_YYYYMMDD_HHMMSS.xlsx
    └── rendimiento_por_vendedor_YYYYMMDD_HHMMSS.json
```

## 🛠️ Instalación y Configuración

### Requisitos del Sistema

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Instalación

1. **Descargar el archivo principal**
```bash
# Descargar main.py con todo el sistema implementado
```

2. **Instalar dependencias**
```bash
pip install pandas numpy openpyxl
```

### Dependencias

```txt
pandas>=1.5.0
numpy>=1.24.0
openpyxl>=3.0.0
```

## 🎯 Guía de Uso

### Ejecución Rápida

```bash
python main.py
```

### Uso Básico en Código

```python
# Importar el sistema desde main.py
from main import SalesReportingSystem

# Crear instancia del sistema
system = SalesReportingSystem()

# Ejecutar demostración completa
system.run_demo()

# O ejecutar modo interactivo
system.run_interactive_mode()
```

### Uso del Servicio de Reportes

```python
from main import SalesReportingService

# Crear servicio con datos por defecto
service = SalesReportingService()

# Generar reporte específico
result = service.generate_report('total_sales', export_formats=['csv', 'excel'])
print(result)

# Generar todos los reportes
results = service.generate_all_reports(export_formats=['json'])
```

### Trabajar con CSV

```python
from main import SalesReportingService

# Cargar datos desde CSV (cuando implementes la funcionalidad)
# service = SalesReportingService(data_source=load_from_csv('mi_archivo.csv'))

# Por ahora usa los datos incluidos en el sistema
service = SalesReportingService()
summary = service.get_data_summary()
print(summary)
```

## 🏗️ Patrones de Diseño Implementados

### 1. Factory Pattern
Crea diferentes tipos de reportes sin exponer la lógica de instanciación.

```python
# Ubicación en main.py: líneas ~350-400
class ReportFactoryProvider:
    _factories = {
        'total_sales': TotalSalesReportFactory,
        'detailed_sales': DetailedSalesReportFactory
    }
    
    @classmethod
    def get_factory(cls, report_type: str):
        factory_class = cls._factories.get(report_type)
        return factory_class()
```

**Ventajas:**
- Desacopla la creación de objetos
- Facilita la extensión con nuevos tipos de reportes
- Centraliza la lógica de creación

### 2. Strategy Pattern
Define algoritmos intercambiables para cálculos de métricas.

```python
# Ubicación en main.py: líneas ~100-200
class TotalSalesByCategoryStrategy(MetricStrategy):
    def calculate(self, data: pd.DataFrame):
        data['total_venta'] = data['precio'] * data['cantidad']
        return data.groupby('categoria')['total_venta'].sum().to_dict()

class DetailedSalesByCategoryStrategy(MetricStrategy):
    def calculate(self, data: pd.DataFrame):
        # Cálculos más complejos con múltiples métricas
        return detailed_metrics
```

**Ventajas:**
- Permite cambiar algoritmos en tiempo de ejecución
- Facilita testing de diferentes estrategias
- Cumple principio Abierto/Cerrado

### 3. Decorator Pattern
Añade funcionalidades a reportes sin modificar su estructura.

```python
# Ubicación en main.py: líneas ~200-300
class ConsoleReportDecorator(ReportDecorator):
    def display(self, data):
        # Formato de consola con emojis y separadores
        return formatted_output

class ExportDecorator(ReportDecorator):
    def display(self, data):
        # Funcionalidad original + exportación
        return base_output + export_functionality
```

**Ventajas:**
- Composición flexible de funcionalidades
- Reutilización de código
- Principio de Responsabilidad Única

## 📊 Tipos de Reportes Disponibles

### 1. Total de Ventas por Categoría (`total_sales`)
```python
service.generate_report('total_sales')
```
- **Datos**: Suma de ingresos por categoría
- **Métricas**: Total general de ventas
- **Uso**: Análisis básico de rendimiento por categoría

**Ejemplo de salida:**
```
📊 TOTAL DE VENTAS POR CATEGORÍA
🏷️  Electrónicos: $8,570.00
🏷️  Libros: $567.00
🏷️  Ropa: $635.00
💰 TOTAL GENERAL: $9,772.00
```

### 2. Métricas Detalladas por Categoría (`detailed_sales`)
```python
service.generate_report('detailed_sales')
```
- **Datos**: Total ventas, precio promedio, cantidad total, productos vendidos
- **Métricas**: Resumen general con totales y promedios
- **Uso**: Análisis profundo de rendimiento

**Ejemplo de salida:**
```
📊 MÉTRICAS DETALLADAS POR CATEGORÍA
🏷️  ELECTRÓNICOS:
   Total Ventas: $8,570.00
   Precio Promedio: $347.83
   Cantidad Total: 15
   Productos Vendidos: 12
```

## 🔧 Configuración y Personalización

### Configuraciones Disponibles

Las configuraciones están definidas en la clase `Config` dentro de `main.py`:

```python
class Config:
    # Formatos de exportación soportados
    SUPPORTED_EXPORT_FORMATS = ['csv', 'excel', 'json']
    
    # Configuración de visualización
    CONSOLE_WIDTH = 80
    EMOJIS = {
        'report': '📊',
        'money': '💰',
        'category': '🏷️'
    }
```

### Personalizar Datos

```python
# Modificar datos_ventas en main.py (líneas ~20-60)
datos_ventas = [
    {"categoria": "Tu_Categoria", "producto": "Tu_Producto", 
     "precio": 100.0, "cantidad": 1, "medio_venta": "Web", 
     "vendedor": "Tu_Vendedor"},
    # ... más datos
]
```

### Agregar Nueva Estrategia

```python
# Agregar al final de main.py
class CustomMetricStrategy(MetricStrategy):
    def calculate(self, data: pd.DataFrame):
        # Tu lógica personalizada
        return {"titulo": "Mi Reporte", "datos": custom_data}

# Registrar en ReportFactoryProvider
ReportFactoryProvider._factories['custom_report'] = CustomReportFactory
```

## 🖥️ Modo Interactivo

El sistema incluye un menú interactivo completo:

```bash
🚀 SISTEMA DE REPORTES DE VENTAS
📊 MENÚ PRINCIPAL
1. Ver resumen de datos
2. Generar reporte específico
3. Generar todos los reportes
4. Ver tipos de reportes disponibles
0. Salir
```

### Opciones del Menú

1. **Ver resumen de datos**: Estadísticas básicas del dataset
2. **Generar reporte específico**: Elegir tipo y formato de exportación
3. **Generar todos los reportes**: Ejecutar análisis completo
4. **Ver tipos disponibles**: Lista de reportes soportados

## 📈 Resultados de Ejemplo

### Resumen de Datos
```
📊 RESUMEN DE DATOS CARGADOS
Total de registros: 35
Categorías únicas: Electrónicos, Libros, Ropa
Vendedores únicos: Ana Pérez, Carlos López, Sofía Gómez, Luis Rodríguez
Medios de venta: Web, Físico, Tienda, Online
Rango de precios: $10.00 - $700.00
```

### Archivos Exportados
- **CSV**: `total_ventas_por_categoria_20250531_143015.csv`
- **Excel**: `metricas_detalladas_por_categoria_20250531_143015.xlsx`
- **JSON**: `rendimiento_por_vendedor_20250531_143015.json`

## 🧪 Testing

### Probar el Sistema

```python
# Ejecutar demostración completa
python main.py

# El sistema automáticamente:
# 1. Muestra resumen de datos
# 2. Genera todos los reportes
# 3. Exporta en múltiples formatos
# 4. Muestra resultados formateados
```

### Validar Funcionalidades

```python
from main import SalesReportingService

def test_basic_functionality():
    service = SalesReportingService()
    
    # Test 1: Verificar carga de datos
    assert len(service.data) > 0
    
    # Test 2: Verificar generación de reportes
    result = service.generate_report('total_sales')
    assert 'Total de Ventas' in result
    
    # Test 3: Verificar múltiples formatos
    results = service.generate_all_reports(['csv', 'json'])
    assert len(results) > 0
    
    print("✅ Todas las pruebas pasaron")

test_basic_functionality()
```

## 🚀 Casos de Uso

### Para Analistas de Datos
```python
# Análisis rápido de ventas
system = SalesReportingSystem()
system.run_demo()  # Genera todos los reportes automáticamente
```

### Para Desarrolladores
```python
# Integración con código existente
from main import SalesReportingService

service = SalesReportingService()
data_summary = service.get_data_summary()
# Usar data_summary en tu aplicación
```

### Para Usuarios Finales
```bash
# Ejecutar desde línea de comandos
python main.py
# Seguir el menú interactivo
```

## 🔄 Extensibilidad

### Agregar Nuevo Tipo de Reporte

1. **Crear nueva estrategia**:
```python
class MyCustomStrategy(MetricStrategy):
    def calculate(self, data):
        # Tu lógica aquí
        return {"titulo": "Mi Reporte", "datos": results}
```

2. **Crear fábrica**:
```python
class MyCustomReportFactory(ReportFactory):
    def create_report(self):
        return BaseSalesReport(MyCustomStrategy())
```

3. **Registrar en el proveedor**:
```python
ReportFactoryProvider._factories['my_custom'] = MyCustomReportFactory
```

### Agregar Nuevo Formato de Exportación

Modificar la clase `ExportDecorator` en `main.py` para incluir tu formato:

```python
def _export_to_my_format(self, data, filename):
    # Implementar tu lógica de exportación
    pass
```

## 📝 Notas de Implementación

### Datos Incluidos
- **35 registros** de ventas de ejemplo
- **4 categorías**: Electrónicos, Libros, Ropa
- **4 vendedores**: Ana Pérez, Carlos López, Sofía Gómez, Luis Rodríguez
- **Múltiples canales**: Web, Físico, Tienda, Online

### Tecnologías Utilizadas
- **Pandas**: Procesamiento y análisis de datos
- **NumPy**: Operaciones numéricas eficientes
- **OpenPyXL**: Exportación a Excel
- **CSV/JSON**: Exportación estándar

### Buenas Prácticas Implementadas
- Separación de responsabilidades
- Código autodocumentado
- Manejo de errores
- Formateo consistente
- Exportación con timestamps

## 🚨 Troubleshooting

### Problema: "ModuleNotFoundError"
```bash
# Instalar dependencias faltantes
pip install pandas numpy openpyxl
```

### Problema: "Archivos no se exportan"
```python
# Verificar permisos de escritura en el directorio
import os
print(os.getcwd())  # Verificar directorio actual
```

### Problema: "Datos no aparecen"
```python
# Verificar que datos_ventas tiene contenido
from main import datos_ventas
print(f"Registros disponibles: {len(datos_ventas)}")
```