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

---

## 🚀 Instalación

### 🔧 Requisitos

- Python 3.8+
- MySQL 8.0+
- Git

### ⚙️ Pasos

```bash
# 1. Clonar el repositorio
git clone <url-del-repo>
cd sistema_ventas_comestibles

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate.bat     # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar archivo .env
cp .env.example .env
# Editar .env con tus credenciales de MySQL

# 5. Crear estructura de base de datos
mysql -u root -p < sql/create_tables.sql

# 6. Cargar datos (si ya tenés configuradas las rutas)
mysql -u root -p < sql/load_data.sql

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

---

## 💹 Análisis de Rendimiento y Escalabilidad

- Índices para optimizar filtros y joins
- Consultas con agregaciones bien estructuradas
- Uso de patrones que facilitan escalar a microservicios
- Patrón Singleton para conexión eficiente y segura

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
