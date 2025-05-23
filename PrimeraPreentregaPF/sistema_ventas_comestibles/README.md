# Sistema de Análisis de Ventas - Tienda de Comestibles

## Descripción del Proyecto

Sistema robusto y escalable desarrollado para una cadena de tiendas de comestibles que opera en múltiples ciudades del país. El sistema permite procesar datos de ventas desde archivos CSV, almacenarlos en una base de datos relacional MySQL y realizar análisis avanzados mediante consultas SQL y modelado orientado a objetos en Python.

## ¿Qué se hizo?

### 1. **Arquitectura del Sistema**
- Diseño de base de datos relacional con 7 tablas interconectadas
- Implementación del patrón MVC (Modelo-Vista-Controlador)
- Aplicación del patrón Singleton para conexiones de base de datos
- Separación de responsabilidades en capas (models, services, database)

### 2. **Modelado de Datos**
- **7 entidades principales**: Countries, Cities, Categories, Products, Customers, Employees, Sales
- **Relaciones complejas**: Claves foráneas y referencias cruzadas
- **Integridad referencial**: Constraints y validaciones a nivel de base de datos

### 3. **Programación Orientada a Objetos**
- **Encapsulamiento**: Atributos privados con getters/setters
- **Validación de datos**: Setters con lógica de validación
- **Métodos de negocio**: Funcionalidades específicas del dominio
- **Herencia y polimorfismo**: Aplicados donde corresponde

### 4. **Servicios de Análisis**
- **AnalyticsService**: Clase especializada en análisis avanzados
- **Métricas de rendimiento**: Por empleado, producto, región
- **Segmentación de clientes**: Basada en comportamiento de compra
- **Dashboard ejecutivo**: Métricas clave para toma de decisiones

### 5. **Testing Comprehensivo**
- **Pruebas unitarias**: Para todos los modelos principales
- **Cobertura de casos**: Positivos y negativos
- **Validación de lógica**: Métodos de negocio y cálculos

## ¿Cómo está organizado el proyecto?
### **Organización por Capas:**

1. **Capa de Datos (data/)**: Archivos CSV con datos de muestra
2. **Capa de Persistencia (sql/)**: Scripts para estructura y carga de datos
3. **Capa de Modelos (src/models/)**: Entidades de dominio con lógica de negocio
4. **Capa de Servicios (src/services/)**: Lógica compleja y análisis
5. **Capa de Acceso a Datos (src/database/)**: Conexión y operaciones de BD
6. **Capa de Pruebas (tests/)**: Validación y testing del sistema

## Justificación Técnica

### **1. Decisiones Arquitectónicas**

#### **Patrón Singleton para Conexión de BD**
```python
class DatabaseConnection:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance
Justificación: Evita múltiples conexiones innecesarias, mejora performance y asegura consistencia.
Encapsulamiento Estricto
pythonclass Product:
    def __init__(self, product_id: int, product_name: str, price: float):
        self.__product_id = product_id        # Atributo privado
        self.__product_name = product_name    # Atributo privado
        self.__price = Decimal(str(price))    # Atributo privado
    
    @property
    def price(self) -> Decimal:               # Getter controlado
        return self.__price
    
    @price.setter
    def price(self, price: float):            # Setter con validación
        if price > 0:
            self.__price = Decimal(str(price))
        else:
            raise ValueError("El precio debe ser mayor a 0")
```python

Justificación: Protege la integridad de los datos y permite validación en tiempo de ejecución.
Uso de Decimal para Montos
pythonself.__price = Decimal(str(price))
Justificación: Evita errores de precisión en cálculos financieros que ocurren con float.
2. Decisiones de Base de Datos
Normalización Completa

1FN: Todos los atributos son atómicos
2FN: No hay dependencias parciales
3FN: No hay dependencias transitivas

Índices Estratégicos
sqlCREATE INDEX idx_sales_date ON sales(SalesDate);
CREATE INDEX idx_sales_customer ON sales(CustomerID);
CREATE INDEX idx_sales_product ON sales(ProductID);
Justificación: Mejora significativamente el performance de consultas frecuentes.
Claves Foráneas con Cascada
sqlFOREIGN KEY (CustomerID) REFERENCES customers(CustomerID)
Justificación: Mantiene integridad referencial y previene datos huérfanos.
3. Decisiones de Diseño de Código
Separación de Responsabilidades

Models: Solo lógica de dominio y validación
Services: Lógica de negocio compleja y análisis
Database: Solo acceso a datos

Manejo de Errores Robusto
pythontry:
    connection = self.connect()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(query, params)
    return cursor.fetchall()
except Error as e:
    self.logger.error(f"Error ejecutando consulta: {e}")
    raise
finally:
    if cursor:
        cursor.close()
Justificación: Asegura liberación de recursos y logging de errores.
Uso de Type Hints
pythondef get_sales_performance_by_employee(self, start_date: datetime = None, 
                                    end_date: datetime = None) -> List[Dict]:
Justificación: Mejora legibilidad, facilita debugging y habilita validación estática.
4. Patrones de Diseño Implementados
Repository Pattern
python@classmethod
def find_by_id(cls, product_id: int) -> Optional['Product']:
    db = DatabaseConnection()
    query = "SELECT * FROM products WHERE ProductID = %s"
    result = db.execute_query(query, (product_id,))
    # ... lógica de mapeo
Factory Pattern (implícito en métodos de clase)
python@classmethod
def get_all(cls) -> List['Country']:
    # Crea múltiples instancias desde datos de BD
Service Layer Pattern
pythonclass AnalyticsService:
    def get_sales_performance_by_employee(self):
        # Lógica compleja de análisis
    
    def get_geographic_sales_analysis(self):
        # Análisis geográfico especializado
Instalación y Uso
Prerrequisitos

Python 3.8+
MySQL 8.0+
Git

Instalación
bash# 1. Clonar repositorio
git clone <url-del-repositorio>
cd sistema_ventas_comestibles

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales de BD

# 5. Crear base de datos
mysql -u root -p < sql/create_tables.sql

# 6. Cargar datos (ajustar rutas en load_data.sql)
mysql -u root -p < sql/load_data.sql
Uso Básico
pythonfrom src.models.product import Product
from src.models.sale import Sale
from src.services.analytics_service import AnalyticsService

# Crear producto
producto = Product(1, "Manzanas", 2.50, 1, "Premium")
print(producto.apply_discount(10))  # Aplicar 10% descuento

# Análisis de ventas
analytics = AnalyticsService()
dashboard = analytics.generate_executive_dashboard()
print(dashboard['general_metrics'])
Ejecutar Pruebas
bash# Todas las pruebas
pytest tests/ -v

# Pruebas específicas
pytest tests/test_models.py -v

# Con cobertura
pytest tests/ --cov=src
Análisis de Rendimiento
El sistema está optimizado para:

Consultas frecuentes: Índices en campos de búsqueda común
Joins complejos: Estructura normalizada pero eficiente
Análisis masivos: Consultas optimizadas con agregaciones
Concurrencia: Patrón Singleton con manejo thread-safe

Escalabilidad
El diseño permite fácil escalabilidad mediante:

Sharding horizontal: Por región geográfica
Réplicas de lectura: Para análisis intensivos
Cache: Redis para consultas frecuentes
Microservicios: Cada modelo puede evolucionar independientemente

Contribución

Fork del proyecto
Crear rama feature (git checkout -b feature/nueva-funcionalidad)
Commit cambios (git commit -am 'Agregar nueva funcionalidad')
Push a la rama (git push origin feature/nueva-funcionalidad)
Crear Pull Request

Licencia
Este proyecto está bajo la licencia MIT. Ver LICENSE para más detalles.
Autor
Romina Cattaneo
Data Engineer
Email: romica44@gmail.com
LinkedIn: [url](https://www.linkedin.com/in/romina-paola-cattaneo-9757b345/)
