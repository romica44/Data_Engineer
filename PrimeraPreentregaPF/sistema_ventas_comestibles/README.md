# Sistema de Análisis de Ventas - Tienda de Comestibles

## 📌 Descripción del Proyecto

Sistema robusto y escalable desarrollado para una cadena de tiendas de comestibles con presencia nacional. Permite:

- Procesar archivos CSV
- Almacenar datos en MySQL
- Realizar análisis avanzados con consultas SQL
- Consultar métricas desde modelos orientados a objetos en Python

---

## 🔧 ¿Qué se hizo?

### 🧱 Arquitectura del Sistema
- Diseño de base de datos relacional con 7 tablas normalizadas
- Patrón MVC y patrón Singleton en conexión a la BD
- Separación por capas: models, services, database, tests, utils

### 🧬 Modelado de Datos
- Entidades: `Countries`, `Cities`, `Categories`, `Products`, `Customers`, `Employees`, `Sales`
- Relaciones con claves foráneas, integridad referencial y normalización 3FN

### 🧠 Programación Orientada a Objetos
- Encapsulamiento con atributos privados y setters con validación
- Métodos de negocio específicos
- Uso de `Decimal` para precisión en cálculos monetarios

<<<<<<< HEAD
### 📈 Servicios de Análisis
- `AnalyticsService`: agrupa lógica analítica compleja
- Métricas por producto, empleado, región, cliente, descuentos
- Generación de dashboard ejecutivo por consola

### 🧪 Testing
- Pruebas unitarias para modelos y servicios
- Casos positivos y negativos
- Cobertura con `pytest` y `--cov`

---

## 🗂 Estructura del Proyecto

```plaintext
sistema_ventas_comestibles/
├── data/
│   ├── countries.csv
│   ├── cities.csv
│   └── ...
├── sql/
│   ├── create_tables.sql
│   ├── load_data.sql
│   └── analysis_queries.sql
├── src/
│   ├── models/
│   ├── services/
│   ├── database/
│   └── utils/
├── tests/
│   ├── test_models.py
│   ├── test_services.py
│   └── test_integration.py
├── config/
│   ├── .env
│   └── .gitignore
├── requirements.txt
├── setup.py
└── main.py
```

---
=======
## ¿Cómo está organizado el proyecto?
### **Organización por Capas:**
>>>>>>> a61308cf1cabb79a0e78436ea3f32b2ca182c2f6

## 🧠 Justificación Técnica

### Arquitectura y Diseño
- **Singleton** en `DatabaseConnection`: evita conexiones duplicadas
- **Encapsulamiento fuerte** en modelos: protección de atributos
- **Decimal** en montos: evita errores por uso de `float`
- **Patrones usados**: Repository, Factory, Service Layer

### Base de Datos
- Normalización: 1FN, 2FN, 3FN
- Índices estratégicos:
  ```sql
  CREATE INDEX idx_sales_date ON sales(SalesDate);
  ```
- Foreign Keys con `ON DELETE CASCADE` para integridad

<<<<<<< HEAD
---
=======
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


Justificación: Protege la integridad de los datos y permite validación en tiempo de ejecución.
Uso de Decimal para Montos
pythonself.__price = Decimal(str(price))
Justificación: Evita errores de precisión en cálculos financieros que ocurren con float.
```

### **2. Decisiones de Base de Datos**
### Normalización Completa
>>>>>>> a61308cf1cabb79a0e78436ea3f32b2ca182c2f6

## 🚀 Instalación

<<<<<<< HEAD
### 🔧 Requisitos
=======
### Índices Estratégicos
sqlCREATE INDEX idx_sales_date ON sales(SalesDate);
CREATE INDEX idx_sales_customer ON sales(CustomerID);
CREATE INDEX idx_sales_product ON sales(ProductID);
Justificación: Mejora significativamente el performance de consultas frecuentes.
Claves Foráneas con Cascada
sqlFOREIGN KEY (CustomerID) REFERENCES customers(CustomerID)
Justificación: Mantiene integridad referencial y previene datos huérfanos.
### **3. Decisiones de Diseño de Código**
### Separación de Responsabilidades
>>>>>>> a61308cf1cabb79a0e78436ea3f32b2ca182c2f6

- Python 3.8+
- MySQL 8.0+
- Git

<<<<<<< HEAD
### ⚙️ Pasos

```bash
# 1. Clonar el repositorio
git clone <url-del-repo>
=======
### Manejo de Errores Robusto
```
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
```
### **4. Patrones de Diseño Implementados**
### Repository Pattern
```
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
```
## Instalación y Uso
### Prerrequisitos

Python 3.8+
MySQL 8.0+
Git

## Instalación
bash# 1. Clonar repositorio
git clone <url-del-repositorio>
>>>>>>> a61308cf1cabb79a0e78436ea3f32b2ca182c2f6
cd sistema_ventas_comestibles

## 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate.bat     # Windows

## 3. Instalar dependencias
pip install -r requirements.txt

<<<<<<< HEAD
# 4. Configurar archivo .env
cp .env.example .env
# Editar .env con tus credenciales de MySQL

# 5. Crear estructura de base de datos
mysql -u root -p < sql/create_tables.sql

# 6. Cargar datos (si ya tenés configuradas las rutas)
=======
## 4. Configurar variables de entorno
cp .env.example .env
### Editar .env con tus credenciales de BD

## 5. Crear base de datos
mysql -u root -p < sql/create_tables.sql

## 6. Cargar datos (ajustar rutas en load_data.sql)
>>>>>>> a61308cf1cabb79a0e78436ea3f32b2ca182c2f6
mysql -u root -p < sql/load_data.sql

<<<<<<< HEAD
# 7. Ejecutar la app
python main.py
```

---

## 🧪 Ejecutar Pruebas

```bash
# Todas las pruebas
pytest tests/ -v

# Con cobertura
pytest --cov=src
```
=======
## Crear producto
producto = Product(1, "Manzanas", 2.50, 1, "Premium")
print(producto.apply_discount(10))  # Aplicar 10% descuento

## Análisis de ventas
analytics = AnalyticsService()
dashboard = analytics.generate_executive_dashboard()
print(dashboard['general_metrics'])
Ejecutar Pruebas
bash# Todas las pruebas
pytest tests/ -v

## Pruebas específicas
pytest tests/test_models.py -v

## Con cobertura
pytest tests/ --cov=src
Análisis de Rendimiento
El sistema está optimizado para:
>>>>>>> a61308cf1cabb79a0e78436ea3f32b2ca182c2f6

---

<<<<<<< HEAD
## 💹 Análisis de Rendimiento y Escalabilidad
=======
## Escalabilidad
El diseño permite fácil escalabilidad mediante:
>>>>>>> a61308cf1cabb79a0e78436ea3f32b2ca182c2f6

- Índices para optimizar filtros y joins
- Consultas con agregaciones bien estructuradas
- Uso de patrones que facilitan escalar a microservicios
- Patrón Singleton para conexión eficiente y segura

<<<<<<< HEAD
---

## 🙌 Contribución

```bash
# Crear rama
git checkout -b feature/mi-mejora

# Realizar cambios
git commit -am "Agregué X funcionalidad"

# Push y PR
git push origin feature/mi-mejora
```

---

## 📝 Licencia

Este proyecto está bajo licencia MIT. Ver archivo `LICENSE`.

---

## 👩‍💻 Autora

**Romina Cattaneo**  
Data Engineer  
📧 romica44@gmail.com  
🔗 [LinkedIn](https://www.linkedin.com/in/romina-paola-cattaneo-9757b345/)
=======
## Contribución

## Fork del proyecto
Crear rama feature (git checkout -b feature/nueva-funcionalidad)
Commit cambios (git commit -am 'Agregar nueva funcionalidad')
Push a la rama (git push origin feature/nueva-funcionalidad)
Crear Pull Request

### Licencia
Este proyecto está bajo la licencia MIT. Ver LICENSE para más detalles.
Autor
Romina Cattaneo
Data Engineer
Email: romica44@gmail.com
LinkedIn: [url](https://www.linkedin.com/in/romina-paola-cattaneo-9757b345/)
>>>>>>> a61308cf1cabb79a0e78436ea3f32b2ca182c2f6
