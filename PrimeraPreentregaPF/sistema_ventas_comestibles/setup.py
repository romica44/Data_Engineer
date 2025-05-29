from setuptools import setup, find_packages

setup(
    name="grocery_sales_dashboard",
    version="1.0.0",
    description="Sistema de análisis y visualización de ventas para supermercados",
    author="Tu Nombre",
    author_email="tucorreo@ejemplo.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        "certifi==2025.4.26",
        "charset-normalizer==3.4.2",
        "colorama==0.4.6",
        "idna==3.10",
        "iniconfig==2.1.0",
        "mysql-connector==2.2.9",
        "numpy==2.2.6",
        "packaging==25.0",
        "pandas==2.2.2",  # ← corregido de "panda"
        "pluggy==1.6.0",
        "pytest==8.3.5",
        "python-dotenv==1.1.0",
        "requests==2.32.3",
        "setuptools==80.8.0",
        "urllib3==2.4.0"
    ],
    entry_points={
        "console_scripts": [
            "grocery-dashboard=main:main"
        ]
    },
    python_requires=">=3.7",
)