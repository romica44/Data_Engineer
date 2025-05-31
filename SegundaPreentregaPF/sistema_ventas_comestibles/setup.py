from setuptools import setup, find_packages
import os

# Leer README para descripción larga
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Leer requirements.txt para dependencias
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="grocery-sales-analysis-system",
    version="2.0.0",  # Versión 2.0 para segunda entrega
    description="Sistema avanzado de análisis de ventas con patrones de diseño - Segunda Entrega PF",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Romina Cattaneo",
    author_email="romica44@gmail.com",
    url="https://github.com/tu-usuario/sistema-ventas-comestibles",
    
    # Configuración de paquetes
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    
    # Dependencias principales
    install_requires=[
        # Base de datos y ORM
        "sqlalchemy>=2.0.25",
        "mysql-connector-python>=8.2.0",
        "pymysql>=1.1.0",
        
        # Análisis de datos
        "pandas>=2.2.3",
        "numpy>=1.26.3",
        
        # Configuración y entorno
        "python-dotenv>=1.0.0",
        "colorama>=0.4.6",
        
        # Testing
        "pytest>=7.4.4",
        "pytest-cov>=4.1.0",
        "pytest-mock>=3.12.0",
        
        # Notebooks
        "jupyter>=1.0.0",
        "notebook>=7.0.6",
        "ipykernel>=6.27.1",
        
        # Utilidades
        "requests>=2.31.0",
        "setuptools>=69.0.3",
        "packaging>=23.2",
    ],
    
    # Dependencias opcionales para desarrollo
    extras_require={
        "dev": [
            "mypy>=1.8.0",
            "black>=23.12.1",
            "flake8>=7.0.0",
            "sphinx>=7.2.6",
            "sphinx-rtd-theme>=2.0.0",
        ],
        "test": [
            "pytest>=7.4.4",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.12.0",
        ],
        "notebook": [
            "jupyter>=1.0.0",
            "notebook>=7.0.6",
            "ipykernel>=6.27.1",
        ]
    },
    
    # Scripts de línea de comandos
    entry_points={
        "console_scripts": [
            "grocery-sales=main:main",
            "grocery-demo=src.patterns.patterns_demo:main",
            "grocery-test=pytest:main",
        ]
    },
    
    # Clasificadores para PyPI
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Topic :: Office/Business :: Financial",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    
    # Metadatos adicionales
    keywords="sales analysis grocery patterns design mysql sqlalchemy pandas",
    project_urls={
        "Bug Reports": "https://github.com/tu-usuario/sistema-ventas-comestibles/issues",
        "Source": "https://github.com/tu-usuario/sistema-ventas-comestibles",
        "Documentation": "https://github.com/tu-usuario/sistema-ventas-comestibles#readme",
    },
    
    # Requisitos de Python
    python_requires=">=3.8",
    
    # Archivos de datos incluidos
    package_data={
        "": ["*.md", "*.txt", "*.yml", "*.yaml", "*.json"],
        "sql": ["*.sql"],
        "notebooks": ["*.ipynb"],
    },
    
    # Archivos adicionales a incluir
    data_files=[
        ("sql", ["sql/create_tables.sql", "sql/load_data.sql", "sql/analysis_queries.sql"]),
        ("notebooks", ["notebooks/demo_sistema_ventas.ipynb"]),
        (".", ["README.md", "LICENSE", ".env.example"]),
    ],
    
    # Configuración de zip_safe
    zip_safe=False,
)