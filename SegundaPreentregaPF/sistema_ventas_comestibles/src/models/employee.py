from typing import Optional, List
from datetime import date
from src.database.connection import DatabaseConnection

class Employee:
    """Clase que representa a un empleado"""

    def __init__(self, employee_id: Optional[int], first_name: str, middle_initial: Optional[str],
                 last_name: str, birth_date: Optional[date], gender: Optional[str],
                 city_id: int, hire_date: Optional[date]):
        self.__employee_id = employee_id
        self.__first_name = first_name.strip()
        self.__middle_initial = middle_initial.strip().upper() if middle_initial else None
        self.__last_name = last_name.strip()
        self.__birth_date = birth_date
        self.__gender = gender.upper() if gender in ['M', 'F'] else None
        self.__city_id = city_id
        self.__hire_date = hire_date

    # Getters
    @property
    def employee_id(self) -> Optional[int]:
        return self.__employee_id

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
    def birth_date(self) -> Optional[date]:
        return self.__birth_date

    @property
    def gender(self) -> Optional[str]:
        return self.__gender

    @property
    def city_id(self) -> int:
        return self.__city_id

    @property
    def hire_date(self) -> Optional[date]:
        return self.__hire_date

    # Métodos de base de datos
    def save(self) -> int:
        db = DatabaseConnection()
        if self.__employee_id is None:
            query = """
                INSERT INTO employees 
                (FirstName, MiddleInitial, LastName, BirthDate, Gender, CityID, HireDate)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            self.__employee_id = db.execute_insert(query, (
                self.__first_name,
                self.__middle_initial,
                self.__last_name,
                self.__birth_date,
                self.__gender,
                self.__city_id,
                self.__hire_date
            ))
        else:
            query = """
                UPDATE employees SET
                FirstName = %s, MiddleInitial = %s, LastName = %s,
                BirthDate = %s, Gender = %s, CityID = %s, HireDate = %s
                WHERE EmployeeID = %s
            """
            db.execute_update(query, (
                self.__first_name,
                self.__middle_initial,
                self.__last_name,
                self.__birth_date,
                self.__gender,
                self.__city_id,
                self.__hire_date,
                self.__employee_id
            ))
        return self.__employee_id

    @classmethod
    def find_by_id(cls, employee_id: int) -> Optional['Employee']:
        db = DatabaseConnection()
        result = db.execute_query("SELECT * FROM employees WHERE EmployeeID = %s", (employee_id,))
        if result:
            row = result[0]
            return cls(
                row['EmployeeID'], row['FirstName'], row['MiddleInitial'],
                row['LastName'], row['BirthDate'], row['Gender'],
                row['CityID'], row['HireDate']
            )
        return None

    @classmethod
    def get_all(cls) -> List['Employee']:
        db = DatabaseConnection()
        results = db.execute_query("SELECT * FROM employees ORDER BY LastName")
        return [
            cls(row['EmployeeID'], row['FirstName'], row['MiddleInitial'],
                row['LastName'], row['BirthDate'], row['Gender'],
                row['CityID'], row['HireDate'])
            for row in results
        ]

    def __str__(self) -> str:
        return f"{self.__first_name} {self.__last_name}"

    def __repr__(self) -> str:
        return f"Employee(id={self.__employee_id}, name='{self.__first_name} {self.__last_name}')"

    def __eq__(self, other) -> bool:
        if isinstance(other, Employee):
            return self.__employee_id == other.employee_id
        return False