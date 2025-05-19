Sistema de Gestión de Usuarios

Un sistema completo de gestión de usuarios implementado en Python que permite registrar, buscar, listar y eliminar usuarios, con persistencia de datos en archivos JSON y TXT.
Mostrar imagen

Características

✅ Gestión completa de usuarios (CRUD)
🔐 Almacenamiento seguro de contraseñas mediante hash SHA-256
💾 Persistencia de datos en formatos JSON y TXT
🧪 Pruebas unitarias para garantizar la calidad del código
🎨 Interfaz colorida y amigable en consola mediante Colorama
🛡️ Manejo robusto de errores con try/except
📚 Código modular con separación clara de responsabilidades
📋 Validación de datos para garantizar la integridad
📊 Documentación completa del código y la API

Instalación
Prerrequisitos

Python 3.10 o superior
pip (gestor de paquetes de Python)

Pasos de instalación

Clona este repositorio:

bashgit clone https://github.com/romica44/user_manager_app.git
cd user_manager_app

Crea y activa un entorno virtual:

bash# Crear entorno virtual
python -m venv venv

# Activar en Windows
venv\Scripts\activate

# Activar en Linux/Mac
source venv/bin/activate

Instala las dependencias:

bashpip install -r requirements.txt

Crea un archivo .env (opcional):

bashcp .env.example .env
Uso
Iniciar la aplicación
bashpython main.py

Funcionalidades principales

Registrar usuarios: Añade nuevos usuarios con nombre, email y contraseña
Listar usuarios: Muestra todos los usuarios registrados en el sistema
Buscar usuarios: Encuentra usuarios por coincidencia en el nombre
Eliminar usuarios: Elimina usuarios del sistema por su ID
Guardar datos: Exporta la lista de usuarios a archivos JSON o TXT
Cargar datos: Importa usuarios desde archivos previamente guardados

Ejemplo de uso
bash# Tras iniciar la aplicación:

# 1. Registrar un usuario:
# Selecciona la opción 1, luego ingresa nombre, email y contraseña

# 2. Listar usuarios:
# Selecciona la opción 2 para ver todos los usuarios

# 3. Buscar usuario:
# Selecciona la opción 3 e ingresa un término de búsqueda

# 4. Guardar usuarios:
# Selecciona la opción 5, elige un nombre de archivo y formato

Estructura del proyecto

user_manager_app/
│
├── src/
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py         # Configuraciones de la aplicación
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py             # Clase User y métodos relacionados
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   └── user_service.py     # Lógica de negocio para usuarios
│   │
│   └── utils/
│       ├── __init__.py
│       └── file_handler.py     # Utilidades para manejo de archivos
│
├── tests/
│   └── test_user_management.py # Pruebas unitarias
│
├── main.py                     # Punto de entrada de la aplicación
├── requirements.txt            # Dependencias del proyecto
├── .env.example                # Ejemplo de variables de entorno
├── README.md                   # Este archivo
└── .gitignore                  # Archivos ignorados por git

Tecnologías utilizadas

Python 3.10+: Lenguaje de programación principal
Colorama: Colores en la terminal
python-dotenv: Gestión de variables de entorno
Unittest: Framework para pruebas unitarias

Ejecución de pruebas
Para ejecutar las pruebas unitarias:
bashpython -m unittest tests/test_user_management.py
O alternativamente:
bashcd tests
python test_user_management.py

Extensiones y mejoras posibles

 Implementar una interfaz gráfica con TkInter o PyQt
 Agregar una base de datos SQLite para mayor robustez
 Implementar sistema de roles y permisos
 Añadir soporte para autenticación de dos factores
 Desarrollar una API REST para acceso remoto
 Soporte para importar/exportar en formato CSV
 Historial de cambios y registro de actividad


Licencia
Este proyecto está licenciado bajo la Licencia MIT - vea el archivo LICENSE para más detalles.
Contacto
Tu Nombre - romica44@gmail.com
Enlace del proyecto: https://github.com/romica44/user_manager_app
