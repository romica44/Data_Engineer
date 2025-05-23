from typing import List, Optional
from src.database.connection import DatabaseConnection

class Country:
    """Clase que representa un país en el sistema"""
    
    def __init__(self, country_id: int, country_name: str, country_code: str):
        """
        Constructor de la clase Country
        
        Args:
            country_id (int): ID único del país
            country_name (str): Nombre del país
            country_code (str): Código de país (2 caracteres)
        """
        self.__country_id = country_id
        self.__country_name = country_name
        self.__country_code = country_code
        self.__cities = []
        
    # Getters (Encapsulamiento)
    @property
    def country_id(self) -> int:
        return self.__country_id
    
    @property
    def country_name(self) -> str:
        return self.__country_name
    
    @property
    def country_code(self) -> str:
        return self.__country_code
    
    @property
    def cities(self) -> List:
        return self.__cities.copy()
    
    # Setters con validación
    @country_name.setter
    def country_name(self, name: str):
        if len(name.strip()) > 0:
            self.__country_name = name.strip()
        else:
            raise ValueError("El nombre del país no puede estar vacío")
    
    @country_code.setter
    def country_code(self, code: str):
        if len(code.strip()) == 2:
            self.__country_code = code.strip().upper()
        else:
            raise ValueError("El código del país debe tener exactamente 2 caracteres")
    
    # Métodos de negocio
    def add_city(self, city):
        """Agrega una ciudad al país"""
        if city not in self.__cities:
            self.__cities.append(city)
    
    def get_cities_count(self) -> int:
        """Retorna el número de ciudades en el país"""
        return len(self.__cities)
    
    def get_sales_by_country(self) -> List[dict]:
        """Obtiene las ventas totales del país desde la base de datos"""
        db = DatabaseConnection()
        query = """
        SELECT COUNT(s.SalesID) as total_sales, 
               SUM(s.TotalPrice) as total_revenue
        FROM sales s
        JOIN customers cu ON s.CustomerID = cu.CustomerID
        JOIN cities ci ON cu.CityID = ci.CityID
        WHERE ci.CountryID = %s
        """
        return db.execute_query(query, (self.__country_id,))
    
    @classmethod
    def find_by_id(cls, country_id: int) -> Optional['Country']:
        """Busca un país por ID en la base de datos"""
        db = DatabaseConnection()
        query = "SELECT * FROM countries WHERE CountryID = %s"
        result = db.execute_query(query, (country_id,))
        
        if result:
            row = result[0]
            return cls(row['CountryID'], row['CountryName'], row['CountryCode'])
        return None
    
    @classmethod
    def get_all(cls) -> List['Country']:
        """Obtiene todos los países de la base de datos"""
        db = DatabaseConnection()
        query = "SELECT * FROM countries ORDER BY CountryName"
        results = db.execute_query(query)
        
        countries = []
        for row in results:
            countries.append(cls(row['CountryID'], row['CountryName'], row['CountryCode']))
        return countries
    
    def save(self) -> int:
        """Guarda el país en la base de datos"""
        db = DatabaseConnection()
        if self.__country_id is None:
            query = "INSERT INTO countries (CountryName, CountryCode) VALUES (%s, %s)"
            self.__country_id = db.execute_insert(query, (self.__country_name, self.__country_code))
        else:
            query = "UPDATE countries SET CountryName = %s, CountryCode = %s WHERE CountryID = %s"
            db.execute_update(query, (self.__country_name, self.__country_code, self.__country_id))
        return self.__country_id
    
    def __str__(self) -> str:
        return f"{self.__country_name} ({self.__country_code})"
    
    def __repr__(self) -> str:
        return f"Country(id={self.__country_id}, name='{self.__country_name}', code='{self.__country_code}')"
    
    def __eq__(self, other) -> bool:
        if isinstance(other, Country):
            return self.__country_id == other.__country_id