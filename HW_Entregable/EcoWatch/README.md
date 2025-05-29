# Sistema EcoWatch - Monitoreo Ambiental Integrado

### ✨ Características Principales

- 🔄 **Procesamiento en tiempo real** de datos ambientales
- 🗄️ **Base de datos MySQL** con esquema optimizado
- ⚡ **Caché temporal** para consultas ultra-rápidas (O(1))
- 📊 **Reportes ejecutivos** con múltiples estrategias de análisis
- 🚨 **Sistema de alertas** críticas automático
- 🏗️ **Arquitectura modular** y extensible
- 🔌 **API REST** para integración con otros sistemas
- 📈 **Dashboard ejecutivo** en tiempo real

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────┐
│                    Sistema EcoWatch                     │
├─────────────────────────────────────────────────────────┤
│  main.py (Facade Principal)                            │
├─────────────────────┬───────────────────────────────────┤
│  services/          │  reports/         │  models/      │
│  ├─ cache_manager   │  ├─ factory       │  ├─ log       │
│  ├─ log_processor   │  ├─ strategies    │  ├─ sala      │
│  └─ data_sources    │  └─ implementations│  └─ sensor    │
├─────────────────────┼───────────────────┼───────────────┤
│  database/          │  config/          │  utils/       │
│  ├─ connection      │  ├─ settings      │  ├─ decorators│
│  ├─ repositories    │  └─ database      │  └─ validators│
│  └─ migrations      │                   │               │
└─────────────────────┴───────────────────┴───────────────┘
```

### 🎯 Patrones de Diseño Implementados

1. **Factory Pattern**: Creación flexible de reportes
2. **Strategy Pattern**: Intercambio de algoritmos de análisis
3. **Singleton Pattern**: Gestión única del caché temporal
4. **Facade Pattern**: Interfaz simplificada del sistema
5. **Repository Pattern**: Abstracción del acceso a datos
6. **Decorator Pattern**: Funcionalidades transversales (logging, benchmark)

## 🚀 Instalación y Configuración

### Prerrequisitos

- **Python 3.8+**
- **MySQL 8.0+**
- **Git**

### 1. Clonar el Repositorio

```bash
git clone https://github.com/tu-empresa/ecowatch-system.git
cd ecowatch-system
```

### 2. Configurar Entorno Virtual

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Linux/Mac:
source venv/bin/activate
# En Windows:
venv\Scripts\activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Base de Datos MySQL

```sql
-- Conectar a MySQL como root
mysql -u root -p

-- Crear base de datos
CREATE DATABASE ecowatch_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Crear usuario (opcional, para mayor seguridad)
CREATE USER 'ecowatch_user'@'localhost' IDENTIFIED BY 'tu_password_seguro';
GRANT ALL PRIVILEGES ON ecowatch_db.* TO 'ecowatch_user'@'localhost';
FLUSH PRIVILEGES;
```

### 5. Configurar Variables de Entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar configuración
nano .env
```

**Configuración mínima en `.env`:**
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=tu_password_mysql
DB_NAME=ecowatch_db
```

### 6. Inicializar Base de Datos

```bash
# Crear tablas del sistema
python scripts/create_tables.py
```

## 🎮 Uso del Sistema

### Opción 1: Demostración Completa

```bash
# Ejecutar demo con datos simulados
python main.py --demo
```

Esta opción:
- ✅ Inicializa el sistema completo
- 🎭 Genera datos simulados realistas
- 📊 Muestra dashboard ejecutivo
- 📋 Genera todos los tipos de reportes
- 💾 Exporta archivos de ejemplo

### Opción 2: Cargar Datos Reales

```bash
# Cargar desde archivo CSV
python main.py --load-csv logs_ambientales_ecowatch.csv

# O desde JSON
python scripts/load_data.py --file datos.json --format json
```

### Opción 3: Servidor API REST

```bash
# Ejecutar solo la API
python main.py --api-only
```

**Endpoints disponibles:**
- `GET /` - Información del sistema
- `GET /dashboard` - Dashboard ejecutivo
- `GET /salas/{sala_id}` - Estado de sala específica
- `GET /alertas` - Alertas críticas activas
- `GET /reportes/{tipo_reporte}` - Generar reporte específico
- `GET /stats` - Estadísticas del sistema

**Documentación interactiva:** http://localhost:8000/docs

## 📊 Tipos de Reportes Disponibles

### 1. Estado por Sala
```python
from reports import TipoReporte, FactoryReportes

reporte = FactoryReportes.crear_reporte(TipoReporte.ESTADO_POR_SALA)
resultado = reporte.generar(logs)
```

**Incluye:**
- 🏢 Estado actual de cada sala
- 📈 Métricas de período
- 🎯 Recomendaciones específicas

### 2. Alertas Críticas
```python
reporte_alertas = FactoryReportes.crear_reporte(TipoReporte.ALERTAS_CRITICAS)
```

**Incluye:**
- 🚨 Clasificación de alertas por severidad
- ⏰ Análisis temporal de incidentes
- 🎯 Plan de acción específico

### 3. Tendencias Ambientales
```python
from reports import AnalisisTendencias

reporte_tendencias = FactoryReportes.crear_reporte(
    TipoReporte.TENDENCIAS_AMBIENTALES, 
    AnalisisTendencias()
)
```

**Incluye:**
- 📈 Análisis de tendencias temporales
- 🔄 Detección de ciclos y patrones
- 🔮 Predicciones básicas

### 4. Resumen Ejecutivo
```python
reporte_ejecutivo = FactoryReportes.crear_reporte(TipoReporte.RESUMEN_EJECUTIVO)
```

**Incluye:**
- 🎯 KPIs operacionales
- ⚠️ Análisis de riesgos
- 💰 Recomendaciones estratégicas

## 🔧 API Programática

### Integración Básica

```python
from main import SistemaEcoWatch
from services import FuenteCSV

# Inicializar sistema
sistema = SistemaEcoWatch()
sistema.inicializar_sistema()

# Cargar datos
fuente_csv = FuenteCSV('datos.csv')
logs_procesados = sistema.cargar_datos_desde_fuente(fuente_csv)

# Consultar estado
estado_sala = sistema.consultar_estado_sala('Sala_1')
alertas = sistema.obtener_alertas_activas()

# Generar reportes
dashboard = sistema.obtener_dashboard_ejecutivo()
sistema.exportar_reportes_completos()

# Cerrar sistema
sistema.cerrar_sistema()
```

### Agregar Fuente de Datos Personalizada

```python
from services.data_sources import FuenteDatos

class MiFuentePersonalizada:
    def leer_logs(self):
        # Tu lógica de lectura aquí
        return [
            {
                'timestamp': '2025-05-29T10:00:00',
                'sala': 'Sala_Nueva',
                'estado': 'INFO',
                'temperatura': 22.5,
                'humedad': 45.0,
                'co2': 800,
                'mensaje': 'Medición normal'
            }
        ]
    
    def validar_formato(self, data):
        # Tu lógica de validación
        return True

# Usar fuente personalizada
sistema.cargar_datos_desde_fuente(MiFuentePersonalizada())
```

## 📋 Scripts Disponibles

### Gestión de Base de Datos
```bash
# Crear todas las tablas
python scripts/create_tables.py

# Verificar estado de la BD
python scripts/check_db_status.py
```

### Carga de Datos
```bash
# Cargar desde CSV con validación
python scripts/load_data.py --file datos.csv --validate-only

# Cargar en lotes grandes
python scripts/load_data.py --file datos.csv --batch-size 5000

# Crear tablas automáticamente si no existen
python scripts/load_data.py --file datos.csv --create-tables
```

### Demostración
```bash
# Demo completa
python scripts/demo.py

# Demo solo con reportes
python scripts/demo.py --reports-only
```

## 🧪 Testing

### Ejecutar Tests

```bash
# Todos los tests
pytest

# Tests específicos
pytest tests/test_models.py
pytest tests/test_reports.py
pytest tests/test_cache.py

# Con cobertura
pytest --cov=ecowatch_system --cov-report=html
```

### Tests de Integración

```bash
# Test completo del sistema
pytest tests/test_integration.py

# Test de base de datos
pytest tests/test_database.py

# Test de API
pytest tests/test_api.py
```

## 📈 Monitoreo y Logging

### Logs del Sistema

```bash
# Ver logs en tiempo real
tail -f ecowatch_system.log

# Buscar errores
grep "ERROR" ecowatch_system.log

# Logs por fecha
grep "2025-05-29" ecowatch_system.log
```

### Métricas de Rendimiento

```python
# Obtener estadísticas detalladas
stats = sistema.obtener_estadisticas_sistema()
print(f"Uptime: {stats['sistema']['uptime']}")
print(f"Logs procesados: {stats['procesamiento']['logs_procesados']}")
print(f"Eficiencia caché: {stats['cache']['consultas_sala']}")
```

## 🔒 Configuración de Seguridad

### Variables Sensibles

```env
# Generar clave secreta segura
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")

# Configurar contraseñas seguras
DB_PASSWORD=contraseña_muy_segura_123!
SMTP_PASSWORD=password_aplicacion_gmail
```

### Configuración de Producción

```env
# .env para producción
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING

# Base de datos de producción
DB_HOST=mysql-prod-server.empresa.com
DB_USER=ecowatch_prod
DB_PASSWORD=contraseña_produccion_super_segura

# SSL y certificados
SSL_CERT_PATH=/path/to/certificate.crt
SSL_KEY_PATH=/path/to/private.key
```

## 🚀 Deployment

### Docker (Recomendado)

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "main.py", "--api-only"]
```

```bash
# Construir imagen
docker build -t ecowatch:latest .

# Ejecutar contenedor
docker run -p 8000:8000 --env-file .env ecowatch:latest
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  ecowatch:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - mysql
    env_file:
      - .env
    volumes:
      - ./reportes:/app/reportes

  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: password
      MYSQL_DATABASE: ecowatch_db
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql

volumes:
  mysql_data:
```

```bash
# Ejecutar con Docker Compose
docker-compose up -d
```

## 📚 Documentación Técnica

### Decisiones de Arquitectura

1. **MySQL vs PostgreSQL**: Elegimos MySQL por:
   - Mayor familiaridad del equipo
   - Excelente rendimiento para cargas OLTP
   - Ecosistema maduro de herramientas

2. **Caché en Memoria vs Redis**: 
   - Memoria local para MVP (menor latencia)
   - Redis para escalamiento futuro

3. **FastAPI vs Flask**:
   - FastAPI por type hints automáticos
   - Documentación interactiva incluida
   - Mejor rendimiento async

### Optimizaciones Implementadas

- **Índices de BD**: Optimizados para consultas frecuentes
- **Caché temporal**: Estructura de datos O(1) para consultas
- **Conexion pooling**: Reutilización eficiente de conexiones
- **Procesamiento en lotes**: Para cargas masivas de datos


### Standards de Código

- **Black**: Formateo automático
- **Flake8**: Linting de código
- **MyPy**: Type checking estático
- **Tests**: Cobertura mínima 80%

### Agregar Nuevo Tipo de Reporte

```python
# 1. Crear implementación
class MiReportePersonalizado(ReporteBase):
    def generar(self, logs):
        # Tu lógica aquí
        return {"mi_reporte": "datos"}

# 2. Agregar al enum
class TipoReporte(Enum):
    MI_REPORTE = "mi_reporte"

# 3. Registrar en factory
FactoryReportes.registrar_reporte(
    TipoReporte.MI_REPORTE, 
    MiReportePersonalizado
)
```

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.
Autor
Romina Cattaneo
Data Engineer
Email: romica44@gmail.com
LinkedIn: [url](https://www.linkedin.com/in/romina-paola-cattaneo-9757b345/)