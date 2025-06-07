#!/usr/bin/env python3
"""
Script de Instalación Avanzada - Sistema de Ventas con SQL Avanzado
Configura automáticamente toda la infraestructura SQL avanzada
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Optional
import time
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('setup_advanced.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AdvancedSetupManager:
    """Gestiona la instalación completa del sistema SQL avanzado."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.setup_results = {}
        self.start_time = time.time()
        
    def print_banner(self):
        """Muestra banner de inicio."""
        banner = """
        ╔══════════════════════════════════════════════════════════════╗
        ║                                                              ║
        ║   🚀 SISTEMA DE VENTAS - INSTALACIÓN AVANZADA SQL 🚀         ║
        ║                                                              ║
        ║   • Consultas CTE y Funciones Ventana                       ║
        ║   • Objetos SQL (Funciones, Triggers, Vistas)               ║
        ║   • Procedimientos Almacenados                              ║
        ║   • Sistema de Auditoría Automática                         ║
        ║   • Integración Python + SQLAlchemy                         ║
        ║                                                              ║
        ╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)
        logger.info("Iniciando instalación avanzada del sistema")
    
    def check_prerequisites(self) -> bool:
        """Verifica que todos los prerequisitos estén instalados."""
        logger.info("🔍 Verificando prerequisitos...")
        
        prerequisites = {
            'python': {'command': 'python --version', 'min_version': '3.8'},
            'pip': {'command': 'pip --version', 'required': True},
            'mysql': {'command': 'mysql --version', 'required': True},
            'git': {'command': 'git --version', 'required': False}
        }
        
        all_good = True
        
        for name, config in prerequisites.items():
            try:
                result = subprocess.run(
                    config['command'].split(), 
                    capture_output=True, 
                    text=True, 
                    check=True
                )
                version_info = result.stdout.strip()
                logger.info(f"✅ {name}: {version_info}")
                
                # Verificar versión mínima de Python
                if name == 'python' and 'min_version' in config:
                    # Extraer versión de Python
                    import re
                    version_match = re.search(r'(\d+\.\d+)', version_info)
                    if version_match:
                        current_version = float(version_match.group(1))
                        min_version = float(config['min_version'])
                        if current_version < min_version:
                            logger.error(f"❌ Python {config['min_version']}+ requerido, encontrado {current_version}")
                            all_good = False
                
            except (subprocess.CalledProcessError, FileNotFoundError):
                if config.get('required', True):
                    logger.error(f"❌ {name} no encontrado o no funciona correctamente")
                    all_good = False
                else:
                    logger.warning(f"⚠️  {name} no encontrado (opcional)")
        
        if all_good:
            logger.info("✅ Todos los prerequisitos verificados")
        else:
            logger.error("❌ Faltan prerequisitos necesarios")
            
        return all_good
    
    def install_python_dependencies(self) -> bool:
        """Instala dependencias de Python."""
        logger.info("📦 Instalando dependencias de Python...")
        
        try:
            # Actualizar pip primero
            subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], 
                         check=True, capture_output=True)
            logger.info("✅ pip actualizado")
            
            # Instalar dependencias desde requirements.txt
            requirements_file = self.project_root / 'requirements.txt'
            if requirements_file.exists():
                logger.info(f"📋 Instalando desde {requirements_file}")
                subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)], 
                             check=True)
                logger.info("✅ Dependencias Python instaladas")
                return True
            else:
                logger.error(f"❌ Archivo {requirements_file} no encontrado")
                return False
                
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Error instalando dependencias Python: {e}")
            return False
    
    def setup_environment_variables(self) -> bool:
        """Configura variables de entorno."""
        logger.info("🔧 Configurando variables de entorno...")
        
        env_example = self.project_root / '.env.example'
        env_file = self.project_root / '.env'
        
        if not env_example.exists():
            # Crear archivo .env.example
            env_content = """# Configuración de Base de Datos
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=tu_contraseña_mysql
DB_NAME=grocery_sales_db

# Configuración de Logging
LOG_LEVEL=INFO
LOG_FILE=sistema_ventas.log

# Configuración de la Aplicación
APP_ENV=development
DEBUG=True

# Configuración de Seguridad
SECRET_KEY=tu_clave_secreta_aqui

# Configuración de Performance
SQLALCHEMY_POOL_SIZE=10
SQLALCHEMY_POOL_RECYCLE=3600
"""
            with open(env_example, 'w') as f:
                f.write(env_content)
            logger.info("✅ Archivo .env.example creado")
        
        if not env_file.exists():
            # Copiar ejemplo a archivo real
            with open(env_example, 'r') as src, open(env_file, 'w') as dst:
                dst.write(src.read())
            logger.warning("⚠️  Archivo .env creado desde ejemplo. ¡EDÍTALO con tus credenciales!")
            return False  # Usuario debe editar manualmente
        else:
            logger.info("✅ Archivo .env ya existe")
            return True
    
    def verify_database_connection(self) -> bool:
        """Verifica conexión a la base de datos."""
        logger.info("🔗 Verificando conexión a base de datos...")
        
        try:
            # Importar después de instalar dependencias
            sys.path.append(str(self.project_root / 'src'))
            from database.connection import DatabaseConnection
            
            db = DatabaseConnection()
            
            # Intentar conectar
            with db.get_connection() as conn:
                result = conn.execute("SELECT 1 as test").fetchone()
                if result and result[0] == 1:
                    logger.info("✅ Conexión a base de datos exitosa")
                    return True
                else:
                    logger.error("❌ Conexión a base de datos falló")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Error conectando a base de datos: {e}")
            logger.error("💡 Verifica que MySQL esté ejecutándose y las credenciales en .env sean correctas")
            return False
    
    def create_database_structure(self) -> bool:
        """Crea la estructura de base de datos."""
        logger.info("🏗️  Creando estructura de base de datos...")
        
        sql_files = [
            'sql/create_tables.sql',
            'sql/load_data.sql'
        ]
        
        try:
            sys.path.append(str(self.project_root / 'src'))
            from database.connection import DatabaseConnection
            
            db = DatabaseConnection()
            
            for sql_file in sql_files:
                file_path = self.project_root / sql_file
                if file_path.exists():
                    logger.info(f"📄 Ejecutando {sql_file}...")
                    
                    with open(file_path, 'r', encoding='utf-8') as f:
                        sql_content = f.read()
                    
                    # Dividir por statements (separados por ;)
                    statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
                    
                    with db.get_connection() as conn:
                        for stmt in statements:
                            if stmt:
                                try:
                                    conn.execute(stmt)
                                except Exception as e:
                                    # Log warning pero continúa (algunas queries pueden fallar si ya existen)
                                    logger.warning(f"⚠️  Statement warning: {e}")
                        conn.commit()
                    
                    logger.info(f"✅ {sql_file} ejecutado exitosamente")
                else:
                    logger.warning(f"⚠️  Archivo {sql_file} no encontrado")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creando estructura de base de datos: {e}")
            return False
    
    def install_advanced_sql_objects(self) -> bool:
        """Instala objetos SQL avanzados."""
        logger.info("🔥 Instalando objetos SQL avanzados...")
        
        try:
            sys.path.append(str(self.project_root / 'src'))
            from services.advanced_analytics_service import AdvancedAnalyticsService
            
            service = AdvancedAnalyticsService()
            results = service.create_advanced_sql_objects()
            
            success_count = sum(1 for success in results.values() if success)
            total_count = len(results)
            
            logger.info(f"📊 Objetos SQL creados: {success_count}/{total_count}")
            
            for obj_name, success in results.items():
                status = "✅" if success else "❌"
                logger.info(f"   {status} {obj_name}")
            
            if success_count == total_count:
                logger.info("🎉 Todos los objetos SQL avanzados instalados exitosamente")
                return True
            else:
                logger.warning(f"⚠️  {total_count - success_count} objetos fallaron")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error instalando objetos SQL avanzados: {e}")
            return False
    
    def run_tests(self) -> bool:
        """Ejecuta pruebas del sistema."""
        logger.info("🧪 Ejecutando pruebas del sistema...")
        
        try:
            # Ejecutar pruebas básicas
            result = subprocess.run([
                sys.executable, '-m', 'pytest', 
                'tests/', '-v', '--tb=short'
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                logger.info("✅ Todas las pruebas pasaron")
                return True
            else:
                logger.warning("⚠️  Algunas pruebas fallaron")
                logger.warning(f"Output: {result.stdout}")
                logger.warning(f"Errors: {result.stderr}")
                return False
                
        except Exception as e:
            logger.warning(f"⚠️  No se pudieron ejecutar las pruebas: {e}")
            return False
    
    def create_sample_data(self) -> bool:
        """Crea datos de muestra si no existen."""
        logger.info("📊 Verificando datos de muestra...")
        
        try:
            sys.path.append(str(self.project_root / 'src'))
            from database.connection import DatabaseConnection
            
            db = DatabaseConnection()
            
            # Verificar si hay datos
            with db.get_connection() as conn:
                result = conn.execute("SELECT COUNT(*) as count FROM sales").fetchone()
                sales_count = result[0] if result else 0
            
            if sales_count > 0:
                logger.info(f"✅ Datos existentes encontrados: {sales_count:,} ventas")
                return True
            else:
                logger.warning("⚠️  No se encontraron datos de ventas")
                logger.info("💡 Ejecuta los scripts de carga de datos manualmente")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error verificando datos: {e}")
            return False
    
    def generate_test_report(self) -> bool:
        """Genera reporte de prueba del sistema."""
        logger.info("📋 Generando reporte de prueba...")
        
        try:
            sys.path.append(str(self.project_root / 'src'))
            from services.advanced_analytics_service import AdvancedAnalyticsService
            
            service = AdvancedAnalyticsService()
            
            # Ejecutar algunas consultas de prueba
            test_results = {}
            
            try:
                dashboard = service.get_executive_dashboard()
                test_results['dashboard'] = f"✅ Dashboard: {len(dashboard)} empleados"
            except Exception as e:
                test_results['dashboard'] = f"❌ Dashboard: {e}"
            
            try:
                ranking = service.get_employee_performance_ranking(months_back=6)
                test_results['ranking'] = f"✅ Ranking: {len(ranking)} empleados"
            except Exception as e:
                test_results['ranking'] = f"❌ Ranking: {e}"
            
            try:
                audit_log = service.get_sales_audit_log(days_back=7)
                test_results['audit'] = f"✅ Auditoría: {len(audit_log)} registros"
            except Exception as e:
                test_results['audit'] = f"❌ Auditoría: {e}"
            
            # Mostrar resultados
            logger.info("🔍 Resultados de pruebas funcionales:")
            for test_name, result in test_results.items():
                logger.info(f"   {result}")
            
            success_count = sum(1 for result in test_results.values() if result.startswith('✅'))
            total_count = len(test_results)
            
            return success_count == total_count
            
        except Exception as e:
            logger.error(f"❌ Error generando reporte de prueba: {e}")
            return False
    
    def print_summary(self):
        """Muestra resumen final de la instalación."""
        duration = time.time() - self.start_time
        
        summary = f"""
        ╔══════════════════════════════════════════════════════════════╗
        ║                                                              ║
        ║               🎉 INSTALACIÓN COMPLETADA 🎉                   ║
        ║                                                              ║
        ╚══════════════════════════════════════════════════════════════╝
        
        ⏱️  Duración total: {duration:.1f} segundos
        📊 Resultados de instalación:
        """
        
        for step, success in self.setup_results.items():
            status = "✅" if success else "❌"
            summary += f"\n        {status} {step}"
        
        success_count = sum(1 for success in self.setup_results.values() if success)
        total_count = len(self.setup_results)
        
        if success_count == total_count:
            summary += f"""
            
        🎯 INSTALACIÓN EXITOSA - SISTEMA LISTO PARA USAR
        
        🚀 Próximos pasos:
           1. Edita el archivo .env con tus credenciales de MySQL
           2. Ejecuta: python main.py
           3. Abre: jupyter notebook notebooks/advanced_sql_demo.ipynb
           4. Explora el dashboard ejecutivo y análisis SQL avanzado
        
        📚 Documentación:
           • README.md - Guía completa del proyecto
           • notebooks/ - Demostraciones interactivas
           • sql/ - Scripts SQL avanzados
           • src/services/advanced_analytics_service.py - API principal
        """
        else:
            summary += f"""
            
        ⚠️  INSTALACIÓN PARCIAL - {total_count - success_count} PASOS FALLARON
        
        🔧 Pasos de solución:
           1. Revisa el log setup_advanced.log para detalles
           2. Verifica que MySQL esté ejecutándose
           3. Edita .env con credenciales correctas
           4. Ejecuta nuevamente: python setup_advanced.py
        
        💡 Soporte:
           • Revisa la documentación en README.md
           • Verifica prerequisitos del sistema
           • Contacta al soporte técnico si persisten errores
        """
        
        print(summary)
        logger.info(f"Instalación completada - {success_count}/{total_count} pasos exitosos")
    
    def run_installation(self):
        """Ejecuta el proceso completo de instalación."""
        self.print_banner()
        
        # Pasos de instalación
        installation_steps = [
            ("Verificar prerequisitos", self.check_prerequisites),
            ("Instalar dependencias Python", self.install_python_dependencies),
            ("Configurar variables de entorno", self.setup_environment_variables),
            ("Verificar conexión BD", self.verify_database_connection),
            ("Crear estructura BD", self.create_database_structure),
            ("Instalar objetos SQL avanzados", self.install_advanced_sql_objects),
            ("Verificar datos", self.create_sample_data),
            ("Ejecutar pruebas", self.run_tests),
            ("Generar reporte de prueba", self.generate_test_report)
        ]
        
        for step_name, step_function in installation_steps:
            logger.info(f"\n{'='*60}")
            logger.info(f"🔄 {step_name}...")
            logger.info(f"{'='*60}")
            
            try:
                success = step_function()
                self.setup_results[step_name] = success
                
                if success:
                    logger.info(f"✅ {step_name} - EXITOSO")
                else:
                    logger.warning(f"⚠️  {step_name} - FALLIDO O INCOMPLETO")
                    
            except Exception as e:
                logger.error(f"❌ {step_name} - ERROR: {e}")
                self.setup_results[step_name] = False
        
        self.print_summary()


def main():
    """Función principal del script de instalación."""
    try:
        setup_manager = AdvancedSetupManager()
        setup_manager.run_installation()
        
        # Exit code basado en resultados
        success_count = sum(1 for success in setup_manager.setup_results.values() if success)
        total_count = len(setup_manager.setup_results)
        
        if success_count == total_count:
            sys.exit(0)  # Éxito completo
        elif success_count > total_count * 0.7:
            sys.exit(1)  # Éxito parcial
        else:
            sys.exit(2)  # Fallo significativo
            
    except KeyboardInterrupt:
        logger.info("\n🛑 Instalación cancelada por el usuario")
        sys.exit(130)
    except Exception as e:
        logger.error(f"❌ Error fatal en instalación: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()