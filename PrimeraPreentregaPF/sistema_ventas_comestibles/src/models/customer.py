from typing import Optional, List
from src.database.connection import DatabaseConnection

class Customer:
    """Clase que representa un cliente en el sistema"""

    def __init__(self, customer_id: Optional[int], first_name: str, middle_initial: Optional[str],
                 last_name: str, city_id: int, address: Optional[str]):
        """
        Constructor de la clase Customer

        Args:
            customer_id (Optional[int]): ID único del cliente
            first_name (str): Nombre
            middle_initial (Optional[str]): Inicial del segundo nombre
            last_name (str): Apellido
            city_id (int): ID de la ciudad
            address (Optional[str]): Dirección del cliente
        """
        self.__customer_id = customer_id
        self.__first_name = first_name.strip()
        self.__middle_initial = middle_initial.strip() if middle_initial else None
        self.__last_name = last_name.strip()
        self.__city_id = city_id
        self.__address = address.strip() if address else None

    # Propiedades
    @property
    def customer_id(self) -> Optional[int]:
        return self.__customer_id

    @property
    def first_name(self) -> str:
        return self.__first_name

    @property
    def middle_initial(self) -> Optional[str]:
        return self.__middle_initial

    @property
    def last_name(self) -> str:
        return self.__last_name

    @property
    def city_id(self) -> int:
        return self.__city_id

    @property
    def address(self) -> Optional[str]:
        return self.__address

    # Setters con validaciones
    @first_name.setter
    def first_name(self, name: str):
        if name.strip():
            self.__first_name = name.strip()
        else:
            raise ValueError("El nombre no puede estar vacío.")

    @middle_initial.setter
    def middle_initial(self, initial: Optional[str]):
        if initial and len(initial.strip()) == 1:
            self.__middle_initial = initial.strip().upper()
        elif not initial:
            self.__middle_initial = None
        else:
            raise ValueError("La inicial debe tener solo un carácter.")

    @last_name.setter
    def last_name(self, name: str):
        if name.strip():
            self.__last_name = name.strip()
        else:
            raise ValueError("El apellido no puede estar vacío.")

    @city_id.setter
    def city_id(self, cid: int):
        if cid > 0:
            self.__city_id = cid
        else:
            raise ValueError("CityID debe ser un número positivo.")

    @address.setter
    def address(self, addr: Optional[str]):
        self.__address = addr.strip() if addr else None

    # Métodos de base de datos
    def save(self) -> int:
        db = DatabaseConnection()
        if self.__customer_id is None:
            query = """INSERT INTO customers (FirstName, MiddleInitial, LastName, CityID, Address)
                       VALUES (%s, %s, %s, %s, %s)"""
            self.__customer_id = db.execute_insert(query, (
                self.__first_name,
                self.__middle_initial,
                self.__last_name,
                self.__city_id,
                self.__address
            ))
        else:
            query = """UPDATE customers 
                       SET FirstName=%s, MiddleInitial=%s, LastName=%s, CityID=%s, Address=%s 
                       WHERE CustomerID=%s"""
            db.execute_update(query, (
                self.__first_name,
                self.__middle_initial,
                self.__last_name,
                self.__city_id,
                self.__address,
                self.__customer_id
            ))
        return self.__customer_id

    @classmethod
    def find_by_id(cls, customer_id: int) -> Optional['Customer']:
        db = DatabaseConnection()
        query = "SELECT * FROM customers WHERE CustomerID = %s"
        result = db.execute_query(query, (customer_id,))
        if result:
            row = result[0]
            return cls(row['CustomerID'], row['FirstName'], row['MiddleInitial'],
                       row['LastName'], row['CityID'], row['Address'])
        return None

    @classmethod
    def get_all(cls) -> List['Customer']:
        db = DatabaseConnection()
        query = "SELECT * FROM customers ORDER BY LastName"
        results = db.execute_query(query)
        return [
            cls(row['CustomerID'], row['FirstName'], row['MiddleInitial'],
                row['LastName'], row['CityID'], row['Address'])
            for row in results
        ]

    def __str__(self) -> str:
        return f"{self.__first_name} {self.__last_name}"

    def __repr__(self) -> str:
        return f"Customer(id={self.__customer_id}, name='{self.__first_name} {self.__last_name}')"

    def __eq__(self, other) -> bool:
        if isinstance(other, Customer):
            return self.__customer_id == other.customer_id
        return False