from decimal import Decimal
from datetime import date
from typing import Optional, List
from src.database.connection import DatabaseConnection

class Product:
    """Clase que representa un producto en el sistema"""
    
    def __init__(self, product_id: Optional[int], product_name: str, price: float, category_id: int,
                 class_type: str = "Regular", modify_date: Optional[date] = None,
                 resistant: bool = False, is_allergic: bool = False, vitality_days: int = 0):
        self.__product_id = product_id
        self.__product_name = product_name.strip()
        self.__price = Decimal(str(price))
        self.__category_id = category_id
        self.__class_type = class_type
        self.__modify_date = modify_date or date.today()
        self.__resistant = resistant
        self.__is_allergic = is_allergic
        self.__vitality_days = vitality_days

    # Getters
    @property
    def product_id(self) -> Optional[int]:
        return self.__product_id

    @property
    def product_name(self) -> str:
        return self.__product_name

    @property
    def price(self) -> Decimal:
        return self.__price

    @property
    def category_id(self) -> int:
        return self.__category_id

    @property
    def class_type(self) -> str:
        return self.__class_type

    @property
    def modify_date(self) -> date:
        return self.__modify_date

    @property
    def resistant(self) -> bool:
        return self.__resistant

    @property
    def is_allergic(self) -> bool:
        return self.__is_allergic

    @property
    def vitality_days(self) -> int:
        return self.__vitality_days

    # Setters
    @product_name.setter
    def product_name(self, name: str):
        if name.strip():
            self.__product_name = name.strip()
        else:
            raise ValueError("El nombre del producto no puede estar vacío.")

    @price.setter
    def price(self, value: float):
        if value > 0:
            self.__price = Decimal(str(value))
        else:
            raise ValueError("El precio debe ser mayor a cero.")

    @class_type.setter
    def class_type(self, value: str):
        valid = ["Regular", "Premium", "Economy"]
        if value in valid:
            self.__class_type = value
        else:
            raise ValueError(f"Clase inválida. Debe ser una de: {valid}")

    # Lógica de negocio
    def apply_discount(self, percentage: float) -> Decimal:
        if 0 <= percentage <= 100:
            return self.__price * (Decimal(1) - Decimal(percentage) / 100)
        else:
            raise ValueError("El porcentaje debe estar entre 0 y 100.")

    def is_premium(self) -> bool:
        return self.__class_type == "Premium"

    def is_perishable(self) -> bool:
        return self.__vitality_days <= 30

    # Consultas relacionadas
    def get_sales_stats(self) -> dict:
        db = DatabaseConnection()
        query = """
        SELECT COUNT(SalesID) as total_sales,
               SUM(Quantity) as total_units_sold,
               SUM(TotalPrice) as total_revenue,
               AVG(TotalPrice) as avg_sale_price,
               MAX(SalesDate) as last_sale_date
        FROM sales 
        WHERE ProductID = %s
        """
        result = db.execute_query(query, (self.__product_id,))
        return result[0] if result else {}

    def get_top_customers(self, limit: int = 5) -> List[dict]:
        db = DatabaseConnection()
        query = """
        SELECT CONCAT(c.FirstName, ' ', c.LastName) as customer_name,
               SUM(s.Quantity) as total_quantity,
               SUM(s.TotalPrice) as total_spent
        FROM sales s
        JOIN customers c ON s.CustomerID = c.CustomerID
        WHERE s.ProductID = %s
        GROUP BY s.CustomerID
        ORDER BY total_quantity DESC
        LIMIT %s
        """
        return db.execute_query(query, (self.__product_id, limit))

    @classmethod
    def find_by_id(cls, product_id: int) -> Optional['Product']:
        db = DatabaseConnection()
        query = "SELECT * FROM products WHERE ProductID = %s"
        result = db.execute_query(query, (product_id,))
        if result:
            row = result[0]
            return cls(
                row['ProductID'], row['ProductName'], float(row['Price']),
                row['CategoryID'], row['Class'], row['ModifyDate'],
                bool(row['Resistant']), bool(row['IsAllergic']), int(row['VitalityDays'])
            )
        return None

    @classmethod
    def get_by_category(cls, category_id: int) -> List['Product']:
        db = DatabaseConnection()
        query = "SELECT * FROM products WHERE CategoryID = %s ORDER BY ProductName"
        results = db.execute_query(query, (category_id,))
        return [
            cls(
                row['ProductID'], row['ProductName'], float(row['Price']),
                row['CategoryID'], row['Class'], row['ModifyDate'],
                bool(row['Resistant']), bool(row['IsAllergic']), int(row['VitalityDays'])
            )
            for row in results
        ]

    def save(self) -> int:
        db = DatabaseConnection()
        if self.__product_id is None:
            query = """
            INSERT INTO products (ProductName, Price, CategoryID, Class, ModifyDate,
                                  Resistant, IsAllergic, VitalityDays)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            self.__product_id = db.execute_insert(query, (
                self.__product_name, float(self.__price), self.__category_id,
                self.__class_type, self.__modify_date,
                self.__resistant, self.__is_allergic, self.__vitality_days
            ))
        else:
            query = """
            UPDATE products SET ProductName = %s, Price = %s, CategoryID = %s,
                Class = %s, ModifyDate = %s, Resistant = %s,
                IsAllergic = %s, VitalityDays = %s
            WHERE ProductID = %s
            """
            db.execute_update(query, (
                self.__product_name, float(self.__price), self.__category_id,
                self.__class_type, self.__modify_date,
                self.__resistant, self.__is_allergic, self.__vitality_days,
                self.__product_id
            ))
        return self.__product_id

    def __str__(self) -> str:
        return f"{self.__product_name} - ${self.__price:.2f} ({self.__class_type})"

    def __repr__(self) -> str:
        return f"Product(id={self.__product_id}, name='{self.__product_name}', price={self.__price})"

    def __eq__(self, other) -> bool:
        return isinstance(other, Product) and self.__product_id == other.product_id
        return False