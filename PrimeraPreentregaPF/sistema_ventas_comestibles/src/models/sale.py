from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from src.database.connection import DatabaseConnection

class Sale:
    """Clase que representa una venta en el sistema"""

    def __init__(self, sales_id: Optional[int], sales_person_id: int, customer_id: int,
                 product_id: int, quantity: int, discount: float, total_price: float,
                 sales_date: datetime, transaction_number: str):
        self.__sales_id = sales_id
        self.__sales_person_id = sales_person_id
        self.__customer_id = customer_id
        self.__product_id = product_id
        self.__quantity = quantity
        self.__discount = Decimal(str(discount))  # descuento entre 0 y 1 (ej. 0.10 = 10%)
        self.__total_price = Decimal(str(total_price))
        self.__sales_date = sales_date
        self.__transaction_number = transaction_number

    # Getters
    @property
    def sales_id(self) -> Optional[int]:
        return self.__sales_id

    @property
    def sales_person_id(self) -> int:
        return self.__sales_person_id

    @property
    def customer_id(self) -> int:
        return self.__customer_id

    @property
    def product_id(self) -> int:
        return self.__product_id

    @property
    def quantity(self) -> int:
        return self.__quantity

    @quantity.setter
    def quantity(self, quantity: int):
        if quantity > 0:
            self.__quantity = quantity
        else:
            raise ValueError("La cantidad debe ser mayor a 0")

    @property
    def discount(self) -> Decimal:
        return self.__discount

    @discount.setter
    def discount(self, discount: float):
        if 0 <= discount <= 1:
            self.__discount = Decimal(str(discount))
        else:
            raise ValueError("El descuento debe estar entre 0 y 1")

    @property
    def total_price(self) -> Decimal:
        return self.__total_price

    @property
    def sales_date(self) -> datetime:
        return self.__sales_date

    @property
    def transaction_number(self) -> str:
        return self.__transaction_number

    # Métodos de negocio
    def is_discounted(self) -> bool:
        return self.__discount > 0

    def get_discount_amount(self) -> Decimal:
        return self.__total_price * self.__discount

    def is_bulk_sale(self, threshold: int = 10) -> bool:
        return self.__quantity >= threshold

    def get_sale_details(self) -> dict:
        db = DatabaseConnection()
        query = """
        SELECT 
            s.*,
            p.ProductName,
            p.Price as ProductPrice,
            c.CategoryName,
            CONCAT(cu.FirstName, ' ', cu.LastName) as CustomerName,
            CONCAT(e.FirstName, ' ', e.LastName) as SalesPersonName,
            ci.CityName,
            co.CountryName
        FROM sales s
        JOIN products p ON s.ProductID = p.ProductID
        JOIN categories c ON p.CategoryID = c.CategoryID
        JOIN customers cu ON s.CustomerID = cu.CustomerID
        JOIN employees e ON s.SalesPersonID = e.EmployeeID
        JOIN cities ci ON cu.CityID = ci.CityID
        JOIN countries co ON ci.CountryID = co.CountryID
        WHERE s.SalesID = %s
        """
        result = db.execute_query(query, (self.__sales_id,))
        return result[0] if result else {}

    def save(self) -> int:
        db = DatabaseConnection()
        if self.__sales_id is None:
            query = """
            INSERT INTO sales (SalesPersonID, CustomerID, ProductID, Quantity, 
                               Discount, TotalPrice, SalesDate, TransactionNumber) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            self.__sales_id = db.execute_insert(query, (
                self.__sales_person_id, self.__customer_id, self.__product_id,
                self.__quantity, float(self.__discount), float(self.__total_price),
                self.__sales_date, self.__transaction_number
            ))
        return self.__sales_id

    @classmethod
    def find_by_id(cls, sales_id: int) -> Optional['Sale']:
        db = DatabaseConnection()
        query = "SELECT * FROM sales WHERE SalesID = %s"
        result = db.execute_query(query, (sales_id,))
        if result:
            row = result[0]
            return cls(
                row['SalesID'], row['SalesPersonID'], row['CustomerID'],
                row['ProductID'], row['Quantity'], float(row['Discount']),
                float(row['TotalPrice']), row['SalesDate'], row['TransactionNumber']
            )
        return None

    @classmethod
    def get_by_date_range(cls, start_date: datetime, end_date: datetime) -> List['Sale']:
        db = DatabaseConnection()
        query = "SELECT * FROM sales WHERE SalesDate BETWEEN %s AND %s ORDER BY SalesDate"
        results = db.execute_query(query, (start_date, end_date))
        return [
            cls(row['SalesID'], row['SalesPersonID'], row['CustomerID'],
                row['ProductID'], row['Quantity'], float(row['Discount']),
                float(row['TotalPrice']), row['SalesDate'], row['TransactionNumber'])
            for row in results
        ]

    @classmethod
    def get_sales_summary(cls, start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None) -> dict:
        db = DatabaseConnection()
        if start_date and end_date:
            query = """
            SELECT COUNT(*) as total_sales,
                   SUM(TotalPrice) as total_revenue,
                   AVG(TotalPrice) as avg_sale,
                   SUM(Quantity) as total_units_sold,
                   COUNT(DISTINCT CustomerID) as unique_customers
            FROM sales
            WHERE SalesDate BETWEEN %s AND %s
            """
            result = db.execute_query(query, (start_date, end_date))
        else:
            query = """
            SELECT COUNT(*) as total_sales,
                   SUM(TotalPrice) as total_revenue,
                   AVG(TotalPrice) as avg_sale,
                   SUM(Quantity) as total_units_sold,
                   COUNT(DISTINCT CustomerID) as unique_customers
            FROM sales
            """
            result = db.execute_query(query)
        return result[0] if result else {}

    def __str__(self) -> str:
        return f"Venta #{self.__sales_id} - {self.__transaction_number} - ${self.__total_price:.2f}"

    def __repr__(self) -> str:
        return f"Sale(id={self.__sales_id}, total={self.__total_price}, customer_id={self.__customer_id})"

    def __eq__(self, other) -> bool:
        return isinstance(other, Sale) and self.__sales_id == other.sales_id
        return False