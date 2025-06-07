from typing import Optional, List
from src.database.connection import DatabaseConnection

class City:
    """Clase que representa una ciudad registrada en el sistema"""

    def __init__(self, city_id: Optional[int], city_name: str, zipcode: str, country_id: int):
        """
        Constructor de la clase City

        Args:
            city_id (Optional[int]): ID único de la ciudad (puede ser None si es nueva)
            city_name (str): Nombre de la ciudad
            zipcode (str): Código postal
            country_id (int): ID del país al que pertenece la ciudad
        """
        self.__city_id = city_id
        self.__city_name = city_name.strip()
        self.__zipcode = zipcode.strip()
        self.__country_id = country_id

    # Propiedades (encapsulamiento)
    @property
    def city_id(self) -> Optional[int]:
        return self.__city_id

    @property
    def city_name(self) -> str:
        return self.__city_name

    @city_name.setter
    def city_name(self, name: str):
        if len(name.strip()) > 0:
            self.__city_name = name.strip()
        else:
            raise ValueError("El nombre de la ciudad no puede estar vacío.")

    @property
    def zipcode(self) -> str:
        return self.__zipcode

    @zipcode.setter
    def zipcode(self, code: str):
        if len(code.strip()) > 0:
            self.__zipcode = code.strip()
        else:
            raise ValueError("El código postal no puede estar vacío.")

    @property
    def country_id(self) -> int:
        return self.__country_id

    @country_id.setter
    def country_id(self, value: int):
        if value > 0:
            self.__country_id = value
        else:
            raise ValueError("El ID de país debe ser un entero positivo.")

    # Métodos de base de datos
    def save(self) -> int:
        """Guarda o actualiza la ciudad en la base de datos"""
        db = DatabaseConnection()
        if self.__city_id is None:
            query = "INSERT INTO cities (CityName, Zipcode, CountryID) VALUES (%s, %s, %s)"
            self.__city_id = db.execute_insert(query, (self.__city_name, self.__zipcode, self.__country_id))
        else:
            query = "UPDATE cities SET CityName = %s, Zipcode = %s, CountryID = %s WHERE CityID = %s"
            db.execute_update(query, (self.__city_name, self.__zipcode, self.__country_id, self.__city_id))
        return self.__city_id

    @classmethod
    def find_by_id(cls, city_id: int) -> Optional['City']:
        """Busca una ciudad por ID"""
        db = DatabaseConnection()
        result = db.execute_query("SELECT * FROM cities WHERE CityID = %s", (city_id,))
        if result:
            row = result[0]
            return cls(row['CityID'], row['CityName'], row['Zipcode'], row['CountryID'])
        return None

    @classmethod
    def get_all(cls) -> List['City']:
        """Retorna todas las ciudades ordenadas alfabéticamente"""
        db = DatabaseConnection()
        results = db.execute_query("SELECT * FROM cities ORDER BY CityName")
        return [cls(row['CityID'], row['CityName'], row['Zipcode'], row['CountryID']) for row in results]

    def __str__(self) -> str:
        return f"{self.__city_name} ({self.__zipcode})"

    def __repr__(self) -> str:
        return f"City(id={self.__city_id}, name='{self.__city_name}', zipcode='{self.__zipcode}', country_id={self.__country_id})"

    def __eq__(self, other) -> bool:
        if isinstance(other, City):
            return self.__city_id == other.city_id
        return False