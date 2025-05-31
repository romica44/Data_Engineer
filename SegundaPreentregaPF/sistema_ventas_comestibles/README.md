# Sistema de Análisis de Ventas - Tienda de Comestibles

## 📌 Descripción del Proyecto

Sistema robusto y escalable desarrollado para una cadena de tiendas de comestibles con presencia nacional. **Segunda entrega** con implementación de patrones de diseño avanzados, SQLAlchemy y arquitectura empresarial.

### ✨ Características Principales
- Procesar archivos CSV y almacenar en MySQL
- **Patrones de diseño**: Singleton, Factory, Builder, Strategy
- **SQLAlchemy** para manejo robusto de base de datos
- **Pandas DataFrames** como formato estándar de resultados
- Análisis avanzados con consultas dinámicas
- **Pruebas unitarias** completas con pytest
- Consultar métricas desde modelos orientados a objetos

---

## 🏗️ Patrones de Diseño Implementados

### 🔗 Singleton Pattern - `DatabaseConnection`
**📁 Ubicación:** `src/database/connection.py`

#### Problema que Resuelve:
- **Múltiples conexiones innecesarias** a la base de datos
- **Inconsistencia** en configuraciones de conexión
- **Desperdicio de recursos** del sistema

#### Implementación:
```python
class DatabaseConnection:
    _instance = None
    _engine = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance
```

#### Beneficios Obtenidos:
- ✅ **Una sola instancia** de conexión en toda la aplicación
- ✅ **Control centralizado** de recursos de BD con SQLAlchemy
- ✅ **Mejor rendimiento** con pool de conexiones
- ✅ **Thread-safe** y configuración consistente

---

### 🏭 Factory Pattern - `ReportFactory`
**📁 Ubicación:** `src/patterns/report_factory.py`

#### Problema que Resuelve:
- **Complejidad en la creación** de diferentes tipos de reportes
- **Acoplamiento fuerte** entre código cliente y clases concretas
- **Dificultad para agregar** nuevos tipos de reportes

#### Implementación:
```python
class ReportFactory:
    def create_report(self, report_type: ReportType, **kwargs) -> BaseReport:
        return self._report_creators[report_type](**kwargs)
```

#### Tipos de Reportes Soportados:
- 📈 **SalesReport** - Análisis de ventas y tendencias
- 👔 **EmployeeReport** - Rendimiento de empleados
- 📦 **ProductReport** - Análisis de productos
- 🌍 **GeographicReport** - Análisis geográfico

#### Beneficios Obtenidos:
- ✅ **Desacoplamiento** total del código cliente
- ✅ **Fácil extensión** para nuevos tipos de reportes
- ✅ **Principio Open/Closed** respetado

---

### 🔨 Builder Pattern - `SQLQueryBuilder`
**📁 Ubicación:** `src/patterns/query_builder.py`

#### Problema que Resuelve:
- **Consultas SQL complejas** difíciles de construir
- **Constructores con muchos parámetros** opcionales
- **Código repetitivo** para consultas similares

#### Implementación (Fluent Interface):
```python
query = (create_sales_query()
         .with_employee_info()
         .with_sales_metrics()
         .where_between("s.SalesDate", start_date, end_date)
         .group_by("e.EmployeeID", "employee_name")
         .top_performers(10)
         .execute())
```

#### Beneficios Obtenidos:
- ✅ **Fluent Interface** para código expresivo
- ✅ **Reutilización** de componentes de consulta
- ✅ **Parámetros seguros** contra SQL Injection
- ✅ **Specialización** con `SalesQueryBuilder`

---

### 🎯 Strategy Pattern - `AnalysisStrategies`
**📁 Ubicación:** `src/patterns/analysis_strategies.py`

#### Problema que Resuelve:
- **Algoritmos de análisis fijos** e intercambiables
- **Dificultad para agregar** nuevos tipos de análisis
- **Código condicional complejo** para seleccionar algoritmos

#### Estrategias Implementadas:
- 📈 **TrendAnalysisStrategy** - Análisis de tendencias temporales
- 📊 **PerformanceComparisonStrategy** - Comparación de rendimiento
- 👥 **SegmentationStrategy** - Segmentación de clientes

#### Implementación:
```python
# Cambio dinámico de estrategia
analyzer = create_trend_analyzer()
result = analyzer.execute_analysis(period='monthly')

# Cambiar algoritmo en runtime
analyzer.set_strategy(PerformanceComparisonStrategy())
```

#### Beneficios Obtenidos:
- ✅ **Intercambio dinámico** de algoritmos
- ✅ **Extensibilidad** para nuevas estrategias
- ✅ **Testing independiente** de cada estrategia

---

## 🔧 ¿Qué se hizo?

### 🆕 **Mejoras de la Segunda Entrega**
- **SQLAlchemy ORM** reemplaza conexiones directas
- **Pandas DataFrames** como formato estándar de resultados
- **Patrones de diseño**: Singleton, Factory, Builder, Strategy
- **Pruebas unitarias** enfocadas en patrones (pytest)
- **Credenciales seguras** con archivo .env
- **Jupyter Notebook** demostrativo con outputs visibles

### 🧱 Arquitectura del Sistema
- Diseño de base de datos relacional con 7 tablas normalizadas
- **Patrón Singleton** mejorado con SQLAlchemy y pool de conexiones
- **Patrón Factory** para creación flexible de reportes
- **Patrón Builder** para construcción dinámica de consultas
- **Patrón Strategy** para algoritmos intercambiables de análisis
- Separación por capas: models, services, database, patterns, tests

### 🧬 Modelado de Datos
- Entidades: `Countries`, `Cities`, `Categories`, `Products`, `Customers`, `Employees`, `Sales`
- Relaciones con claves foráneas, integridad referencial y normalización 3FN
- **SQLAlchemy ORM** para mapeo objeto-relacional

### 🧠 Programación Orientada a Objetos
- Encapsulamiento con atributos privados y setters con validación
- **Type hints** para mejor documentación del código
- Uso de `Decimal` para precisión en cálculos monetarios
- **Interfaces abstractas** para patrones Strategy

### 📈 Servicios de Análisis
- `AnalyticsService`: **retorna pandas DataFrames** en lugar de listas
- **QueryBuilder** para consultas SQL dinámicas y reutilizables
- **ReportFactory** para generar diferentes tipos de análisis
- **Estrategias de análisis** intercambiables para flexibilidad
- Generación de dashboard ejecutivo por consola

### 🧪 Testing Mejorado
- **Pruebas unitarias** enfocadas en patrones de diseño
- **pytest** configurado con fixtures y mocking
- Casos positivos y negativos para cada patrón
- **TestSingletonPattern**, **TestFactoryPattern**, **TestBuilderPattern**, **TestStrategyPattern**
- Cobertura con `pytest --cov`

---

## 🗂 Estructura del Proyecto

```plaintext
sistema_ventas_comestibles/
├── 📂 data/
│   ├── countries.csv
│   ├── cities.csv
│   └── ... (otros CSVs)
├── 📂 sql/
│   ├── create_tables.sql
│   ├── load_data.sql
│   └── analysis_queries.sql
├── 📂 src/
│   ├── 📂 database/
│   │   ├── __init__.py
│   │   └── connection.py              # 🔗 Singleton Pattern + SQLAlchemy
│   ├── 📂 patterns/                   # 🆕 Patrones de diseño
│   │   ├── __init__.py
│   │   ├── report_factory.py          # 🏭 Factory Pattern
│   │   ├── query_builder.py           # 🔨 Builder Pattern
│   │   ├── analysis_strategies.py     # 🎯 Strategy Pattern
│   │   └── patterns_demo.py           # 🎪 Demostración integrada
│   ├── 📂 models/
│   │   ├── __init__.py
│   │   └── reports.py                 # 📄 Modelos de reportes
│   ├── 📂 services/
│   │   ├── __init__.py
│   │   ├── analytics_service.py       # 📊 Actualizado con DataFrames
│   │   └── helpers.py                 # 🛠️ Utilidades
│   └── 📂 utils/                      # (mantenido de primera entrega)
├── 📂 tests/
│   ├── __init__.py
│   ├── test_patterns.py               # 🆕 Pruebas de patrones de diseño
│   ├── test_models.py                 # (de primera entrega)
│   ├── test_services.py               # (actualizado)
│   └── test_integration.py            # (actualizado)
├── 📂 notebooks/                      # 🆕 Jupyter notebooks
│   └── demo_sistema_ventas.ipynb      # 📓 Demostración completa
├── 📂 config/
│   └── .env                           # 🔐 Credenciales (NO subir al repo)
├── .gitignore                         # 🆕 Actualizado para .env
├── pytest.ini                        # 🆕 Configuración de pytest
├── requirements.txt                   # 🆕 Actualizado con nuevas dependencias
├── setup.py                          # 🆕 Script de instalación automática
├── README.md                         # 📚 Este archivo actualizado
└── main.py                           # 🚀 Punto de entrada (actualizado)
```

---

## 🧠 Justificación Técnica

### Patrones de Diseño Elegidos

#### 🔗 **¿Por qué Singleton para DatabaseConnection?**
- **Problema:** Múltiples instancias de conexión desperdician recursos
- **Solución:** Una sola instancia controla el pool de conexiones SQLAlchemy
- **Beneficio:** Mejor rendimiento, configuración consistente, thread-safety

#### 🏭 **¿Por qué Factory para Reportes?**
- **Problema:** Lógica compleja y dispersa para crear diferentes reportes
- **Solución:** Centralizar creación con factory que encapsula la complejidad
- **Beneficio:** Fácil agregar nuevos reportes sin modificar código existente

#### 🔨 **¿Por qué Builder para Consultas SQL?**
- **Problema:** Consultas complejas con muchos parámetros opcionales
- **Solución:** Construcción fluida paso a paso con method chaining
- **Beneficio:** Código legible, reutilizable y menos propenso a errores

#### 🎯 **¿Por qué Strategy para Análisis?**
- **Problema:** Diferentes algoritmos de análisis según contexto
- **Solución:** Estrategias intercambiables que implementan interfaz común
- **Beneficio:** Extensibilidad, testing independiente, flexibilidad runtime

### Arquitectura y Diseño Mejorados
- **SQLAlchemy ORM**: reemplaza conexiones mysql.connector directas
- **Pandas DataFrames**: formato estándar más potente que listas de diccionarios
- **Type hints**: mejor documentación y IDE support
- **Logging estructurado**: para debugging y monitoreo
- **Principios SOLID**: Single Responsibility, Open/Closed, etc.

### Base de Datos
- Normalización: 1FN, 2FN, 3FN (mantenido de primera entrega)
- **Pool de conexiones SQLAlchemy**: mejor gestión de recursos
- **Parámetros bindados**: prevención de SQL injection
- Índices estratégicos:
  ```sql
  CREATE INDEX idx_sales_date ON sales(SalesDate);
  CREATE INDEX idx_sales_customer ON sales(CustomerID);
  ```

---

## 🚀 Instalación

### 🔧 Requisitos

- Python 3.8+
- MySQL 8.0+
- Git

### ⚙️ Pasos

```bash
# 1. Clonar el repositorio
git clone 
cd sistema_ventas_comestibles

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate          # Windows

# 3. Instalar dependencias (NUEVAS dependencias incluidas)
pip install -r requirements.txt

# 4. Configurar archivo .env (ACTUALIZADO con nuevas variables)
cp .env.example .env
# Editar .env con tus credenciales de MySQL:
# DB_HOST=localhost
# DB_PORT=3306
# DB_USER=tu_usuario_mysql
# DB_PASSWORD=tu_contraseña_mysql
# DB_NAME=grocery_sales_db

# 5. (OPCIONAL) Ejecutar script de instalación automática
python setup.py

# 6. Crear estructura de base de datos
mysql -u root -p < sql/create_tables.sql

# 7. Cargar datos
mysql -u root -p < sql/load_data.sql

# 8. Ejecutar la app (MEJORADA con patrones de diseño)
python main.py

# 9. (NUEVO) Demostrar patrones de diseño
python src/patterns/patterns_demo.py

# 10. (NUEVO) Ejecutar Jupyter notebook
jupyter notebook notebooks/demo_sistema_ventas.ipynb
```

---

## 🧪 Ejecutar Pruebas

```bash
# Todas las pruebas (INCLUYE nuevas pruebas de patrones)
pytest tests/ -v

# Solo pruebas de patrones de diseño
pytest tests/test_patterns.py -v

# Con cobertura completa
pytest --cov=src --cov-report=html

# Pruebas específicas por patrón
pytest tests/test_patterns.py::TestSingletonPattern -v
pytest tests/test_patterns.py::TestFactoryPattern -v
pytest tests/test_patterns.py::TestBuilderPattern -v
pytest tests/test_patterns.py::TestStrategyPattern -v
```

---

## 🚀 Ejemplos de Uso de los Nuevos Patrones

### 1. **Factory Pattern - Crear Reportes**
```python
from src.patterns.report_factory import ReportFactory, ReportType

factory = ReportFactory()

# Crear diferentes tipos de reportes
employee_report = factory.create_report(ReportType.EMPLOYEE)
sales_report = factory.create_report(ReportType.SALES, period='monthly')
product_report = factory.create_report(ReportType.PRODUCT)

print(employee_report.format_for_display())
```

### 2. **Builder Pattern - Consultas Dinámicas**
```python
from src.patterns.query_builder import create_sales_query

# Construir consulta compleja con fluent interface
data = (create_sales_query()
        .with_employee_info()
        .with_sales_metrics()
        .for_period(start_date, end_date)
        .group_by("e.EmployeeID", "employee_name")
        .top_performers(10)
        .execute())  # Retorna pandas DataFrame
```

### 3. **Strategy Pattern - Análisis Intercambiables**
```python
from src.patterns.analysis_strategies import create_trend_analyzer

# Usar estrategia de análisis de tendencias
analyzer = create_trend_analyzer()
result = analyzer.execute_analysis(period='monthly')

# Cambiar estrategia dinámicamente
from src.patterns.analysis_strategies import PerformanceComparisonStrategy
analyzer.set_strategy(PerformanceComparisonStrategy())
comparison_result = analyzer.execute_analysis(comparison_type='employees')
```

### 4. **Singleton + SQLAlchemy - Conexión Única**
```python
from src.database.connection import DatabaseConnection

# Todas las instancias son la misma (Singleton)
db1 = DatabaseConnection()
db2 = DatabaseConnection()
assert db1 is db2  # True

# Ejecutar consulta que retorna DataFrame
df = db1.execute_query_to_dataframe("SELECT * FROM sales LIMIT 10")
print(f"Tipo de resultado: {type(df)}")  # 
```

---

## 💹 Análisis de Rendimiento y Escalabilidad

### Mejoras de Rendimiento:
- **Pool de conexiones SQLAlchemy**: manejo eficiente de múltiples consultas
- **Pandas DataFrames**: operaciones vectorizadas más rápidas
- **Consultas optimizadas** con Builder Pattern
- **Índices estratégicos** en campos frecuentemente consultados
- **Lazy loading** en algunas operaciones

### Escalabilidad:
- **Patrones de diseño** facilitan agregar nuevas funcionalidades
- **Strategy Pattern** permite nuevos algoritmos sin modificar código
- **Factory Pattern** facilita nuevos tipos de reportes
- **Builder Pattern** soporta consultas cada vez más complejas
- **Singleton** controla recursos centralizadamente

---

## 🔐 Seguridad Mejorada

### Credenciales:
- ✅ **Variables de entorno** (.env) - NO hardcodeadas
- ✅ **Archivo .env excluido** del repositorio (.gitignore)
- ✅ **Template .env.example** para guía

### Base de Datos:
- ✅ **SQLAlchemy ORM** previene SQL injection automáticamente
- ✅ **Parámetros bindados** en todas las consultas
- ✅ **Pool de conexiones** controlado y seguro
- ✅ **Validación de entrada** en todos los endpoints

---

## 🆕 Características Nuevas de la Segunda Entrega

### 🏗️ **Patrones de Diseño**
- **Singleton, Factory, Builder, Strategy** completamente implementados
- **Justificación técnica** de cada patrón elegido
- **Documentación completa** de problemas resueltos

### 🔧 **Tecnología**
- **SQLAlchemy** reemplaza mysql.connector
- **Pandas DataFrames** en lugar de listas de diccionarios
- **Type hints** en todo el código
- **Logging estructurado** para mejor debugging

### 🧪 **Testing Robusto**
- **25+ pruebas unitarias** enfocadas en patrones
- **pytest** configurado con fixtures profesionales
- **Mocking** apropiado para testing aislado
- **Cobertura de código** medible

### 📊 **Análisis Avanzado**
- **Estrategias intercambiables** de análisis
- **Construcción dinámica** de consultas SQL
- **Reportes flexibles** con Factory Pattern
- **DataFrames** para análisis más potente

### 📚 **Documentación**
- **Jupyter Notebook** interactivo con demostración completa
- **README actualizado** con justificaciones técnicas
- **Docstrings** completos en todo el código
- **Ejemplos de uso** de cada patrón

---

## 🧪 Ejecutar Demostraciones

```bash
# Demo principal mejorada
python main.py

# Demo específica de patrones de diseño
python src/patterns/patterns_demo.py

# Jupyter notebook interactivo (NUEVO)
jupyter notebook notebooks/demo_sistema_ventas.ipynb

# Verificar que todos los patrones funcionan
python -c "
from src.database.connection import DatabaseConnection
from src.patterns.report_factory import ReportFactory
from src.patterns.query_builder import create_sales_query
from src.patterns.analysis_strategies import create_trend_analyzer
print('✅ Todos los patrones importados correctamente')
"
```

---

## 🙌 Contribución

```bash
# Crear rama para nuevas funcionalidades
git checkout -b feature/nuevo-patron-diseño

# Realizar cambios siguiendo los patrones establecidos
git commit -am "Agregué nuevo patrón Observer para notificaciones"

# Push y PR
git push origin feature/nuevo-patron-diseño
```

### 📋 **Guías para Contribuir:**
- Seguir los **patrones de diseño** establecidos
- Agregar **pruebas unitarias** para nuevas funcionalidades
- Actualizar **documentación** correspondiente
- Usar **type hints** y **docstrings**
- Mantener **cobertura de pruebas** alta

---

## 📝 Licencia

Este proyecto está bajo licencia MIT. Ver archivo `LICENSE`.

---

## 👩‍💻 Autora

**Romina Cattaneo**  
Data Engineer  
📧 romica44@gmail.com  
🔗 [LinkedIn](https://www.linkedin.com/in/romina-paola-cattaneo-9757b345/)

### 🏆 **Segunda Entrega - Patrones de Diseño**
- ✅ **4 patrones de diseño** implementados y justificados
- ✅ **SQLAlchemy + Singleton** para conexión robusta
- ✅ **Pandas DataFrames** como formato estándar
- ✅ **Pruebas unitarias** completas con pytest
- ✅ **Jupyter Notebook** demostrativo
- ✅ **Arquitectura empresarial** escalable y mantenible

---
