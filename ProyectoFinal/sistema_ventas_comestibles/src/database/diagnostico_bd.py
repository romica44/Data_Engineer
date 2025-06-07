#!/usr/bin/env python3
"""
Script de Diagnóstico de Base de Datos
Identifica y resuelve problemas de conexión paso a paso
"""

import os
import sys
import subprocess
import mysql.connector
from mysql.connector import Error as MySQLError
from dotenv import load_dotenv

def print_header(title):
    """Imprime un encabezado bonito"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")

def print_step(step, description):
    """Imprime un paso del diagnóstico"""
    print(f"\n{step}️⃣ {description}")
    print("-" * 40)

def check_python_packages():
    """Verifica que los paquetes necesarios estén instalados"""
    required_packages = [
        'mysql-connector-python',
        'pymysql',
        'sqlalchemy',
        'pandas',
        'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - FALTANTE")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n💡 Para instalar los paquetes faltantes:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_mysql_service():
    """Verifica si MySQL está ejecutándose"""
    try:
        # Intentar conectar al servicio MySQL básico
        connection = mysql.connector.connect(
            host='localhost',
            port=3306,
            user='root',
            password='',
            connect_timeout=5
        )
        connection.close()
        print("✅ MySQL está ejecutándose en localhost:3306")
        return True
    except MySQLError as e:
        if "Access denied" in str(e):
            print("✅ MySQL está ejecutándose (problema de credenciales)")
            return True
        else:
            print(f"❌ MySQL no está disponible: {e}")
            return False

def get_mysql_credentials():
    """Obtiene credenciales interactivamente"""
    print("\n📝 Configuración de credenciales:")
    
    host = input("Host [localhost]: ").strip() or 'localhost'
    port = input("Puerto [3306]: ").strip() or '3306'
    user = input("Usuario [root]: ").strip() or 'root'
    password = input("Contraseña: ")
    
    try:
        port = int(port)
    except ValueError:
        port = 3306
    
    return host, port, user, password

def test_credentials(host, port, user, password):
    """Prueba las credenciales"""
    try:
        connection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            connect_timeout=10
        )
        connection.close()
        print("✅ Credenciales correctas")
        return True
    except MySQLError as e:
        print(f"❌ Credenciales incorrectas: {e}")
        return False

def get_available_databases(host, port, user, password):
    """Lista las bases de datos disponibles"""
    try:
        connection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password
        )
        cursor = connection.cursor()
        cursor.execute("SHOW DATABASES")
        databases = [db[0] for db in cursor.fetchall()]
        cursor.close()
        connection.close()
        
        print("📋 Bases de datos disponibles:")
        for i, db in enumerate(databases, 1):
            print(f"   {i}. {db}")
        
        return databases
    except MySQLError as e:
        print(f"❌ Error obteniendo bases de datos: {e}")
        return []

def create_database_if_needed(host, port, user, password, db_name):
    """Crea la base de datos si no existe"""
    try:
        connection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password
        )
        cursor = connection.cursor()
        
        # Verificar si existe
        cursor.execute("SHOW DATABASES")
        existing_dbs = [db[0] for db in cursor.fetchall()]
        
        if db_name not in existing_dbs:
            print(f"🔧 Creando base de datos '{db_name}'...")
            cursor.execute(f"CREATE DATABASE {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"✅ Base de datos '{db_name}' creada exitosamente")
        else:
            print(f"✅ Base de datos '{db_name}' ya existe")
        
        cursor.close()
        connection.close()
        return True
        
    except MySQLError as e:
        print(f"❌ Error creando base de datos: {e}")
        return False

def create_env_file(host, port, user, password, database):
    """Crea archivo .env con la configuración"""
    env_content = f"""# Configuración de Base de Datos
DB_HOST={host}
DB_PORT={port}
DB_USER={user}
DB_PASSWORD={password}
DB_NAME={database}
"""
    
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("✅ Archivo .env creado exitosamente")
        return True
    except Exception as e:
        print(f"❌ Error creando .env: {e}")
        return False

def test_final_connection(host, port, user, password, database):
    """Prueba la conexión final con SQLAlchemy"""
    try:
        from sqlalchemy import create_engine, text
        
        # Probar diferentes drivers
        drivers = ['mysql+pymysql', 'mysql+mysqlconnector']
        
        for driver in drivers:
            try:
                connection_url = f"{driver}://{user}:{password}@{host}:{port}/{database}"
                engine = create_engine(connection_url)
                
                with engine.connect() as conn:
                    result = conn.execute(text("SELECT 1 as test"))
                    test_value = result.fetchone()[0]
                    
                if test_value == 1:
                    print(f"✅ SQLAlchemy funciona con {driver}")
                    engine.dispose()
                    return True
                    
            except Exception as e:
                print(f"⚠️  {driver} falló: {e}")
        
        return False
        
    except Exception as e:
        print(f"❌ Error probando SQLAlchemy: {e}")
        return False

def main():
    """Función principal del diagnóstico"""
    print_header("DIAGNÓSTICO DE BASE DE DATOS - SISTEMA DE VENTAS")
    print("Este script identificará y resolverá problemas de conexión paso a paso")
    
    # Paso 1: Verificar paquetes Python
    print_step("1", "Verificando paquetes Python requeridos")
    if not check_python_packages():
        print("\n❌ Instala los paquetes faltantes y vuelve a ejecutar este script")
        return False
    
    # Paso 2: Verificar servicio MySQL
    print_step("2", "Verificando servicio MySQL")
    if not check_mysql_service():
        print("\n❌ MySQL no está ejecutándose.")
        print("💡 Soluciones:")
        print("   • Windows: Iniciar XAMPP o WAMP")
        print("   • macOS: brew services start mysql")
        print("   • Linux: sudo systemctl start mysql")
        return False
    
    # Paso 3: Obtener credenciales
    print_step("3", "Configurando credenciales de conexión")
    
    # Intentar cargar desde .env existente
    load_dotenv()
    host = os.getenv('DB_HOST', 'localhost')
    port = int(os.getenv('DB_PORT', 3306))
    user = os.getenv('DB_USER', 'root')
    password = os.getenv('DB_PASSWORD', '')
    
    print(f"Configuración actual:")
    print(f"   Host: {host}")
    print(f"   Puerto: {port}")
    print(f"   Usuario: {user}")
    print(f"   Contraseña: {'***' if password else '(vacía)'}")
    
    # Probar credenciales actuales
    if not test_credentials(host, port, user, password):
        print("\n🔧 Las credenciales actuales no funcionan. Vamos a configurarlas:")
        host, port, user, password = get_mysql_credentials()
        
        if not test_credentials(host, port, user, password):
            print("❌ No se pudo establecer conexión con las credenciales proporcionadas")
            return False
    
    # Paso 4: Verificar/crear base de datos
    print_step("4", "Verificando base de datos")
    databases = get_available_databases(host, port, user, password)
    
    # Buscar base de datos de ventas
    target_databases = ['ventas_comestibles', 'grocery_sales_db', 'ventas', 'sistema_ventas']
    found_db = None
    
    for target_db in target_databases:
        if target_db in databases:
            found_db = target_db
            break
    
    if not found_db:
        print(f"\n🔧 No se encontró base de datos de ventas.")
        print("Opciones:")
        print("1. Crear nueva base de datos 'ventas_comestibles'")
        print("2. Usar base de datos existente")
        
        choice = input("Selecciona opción [1]: ").strip() or "1"
        
        if choice == "1":
            found_db = "ventas_comestibles"
            if not create_database_if_needed(host, port, user, password, found_db):
                return False
        else:
            print("Bases de datos disponibles:")
            for i, db in enumerate(databases, 1):
                print(f"   {i}. {db}")
            
            try:
                db_choice = int(input("Selecciona número: ")) - 1
                found_db = databases[db_choice]
            except (ValueError, IndexError):
                print("❌ Selección inválida")
                return False
    
    print(f"✅ Usando base de datos: {found_db}")
    
    # Paso 5: Crear archivo .env
    print_step("5", "Creando configuración .env")
    if not create_env_file(host, port, user, password, found_db):
        return False
    
    # Paso 6: Prueba final
    print_step("6", "Prueba final de conexión")
    if test_final_connection(host, port, user, password, found_db):
        print("\n🎉 ¡DIAGNÓSTICO COMPLETADO EXITOSAMENTE!")
        print(f"✅ Configuración guardada en .env")
        print(f"✅ Base de datos: {found_db}")
        print(f"✅ SQLAlchemy funcionando")
        print("\n🚀 Ahora puedes ejecutar el sistema principal")
        return True
    else:
        print("\n❌ La prueba final falló")
        print("💡 Verifica que tienes los drivers MySQL instalados:")
        print("   pip install pymysql mysql-connector-python")
        return False

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Diagnóstico cancelado por el usuario")
    except Exception as e:
        print(f"\n💥 Error inesperado: {e}")
        sys.exit(1)