from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from src.database.connection import DatabaseConnection

class Sale:
    """Clase que representa una venta en el sistema"""
    
    def __init__(self, sales_id: int, sales_person_id: int, customer_id: int,
                 product_id: int, quantity: int, discount: float, total_price: float,
                 sales_date: datetime, transaction_number: str,
                 customers_customer_id: int, customers_cities_city_id: int,
                 customers_cities_countries_country_id: int):
        """
        Constructor de la clase Sale
        
        Args:
            sales_id (int): ID único de la venta
            sales_person_id (int): ID del vendedor
            customer_id (int): ID del cliente
            product_id (int): ID del producto
            quantity (int): Cantidad vendida
            discount (float): Descuento aplicado
            total_price (float): Precio total
            sales_date (datetime): Fecha de la venta
            transaction_number (str): Número de transacción
            customers_customer_id (int): ID del cliente (referencia)
            customers_cities_city_id (int): ID de la ciudad del cliente
            customers_cities_countries_country_id (int): ID del país del cliente
        """
        self.__sales_id = sales_id
        self.__sales_person_id = sales_person_id
        self.__customer_id = customer_id
        self.__product_id = product_id
        self.__quantity = quantity
        self.__discount = Decimal(str(discount))
        self.__total_price = Decimal(str(total_price))
        self.__sales_date = sales_date
        self.__transaction_number = transaction_number
        self.__customers_customer_id = customers_customer_id
        self.__customers_cities_city_id = customers_cities_city_id
        self.__customers_cities_countries_country_id = customers_cities_countries_country_id
    
    # Getters (Encapsulamiento)
    @property
    def sales_id(self) -> int:
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
    
    @property
    def discount(self) -> Decimal:
        return self.__discount
    
    @property
    def total_price(self) -> Decimal:
        return self.__total_price
    
    @property
    def sales_date(self) -> datetime:
        return self.__sales_date
    
    @property
    def transaction_number(self) -> str:
        return self.__transaction_number
    
    # Setters con validación
    @quantity.setter
    def quantity(self, quantity: int):
        if quantity > 0:
            self.__quantity = quantity
            self._recalculate_total()
        else:
            raise ValueError("La cantidad debe ser mayor a 0")
    
    @discount.setter
    def discount(self, discount: float):
        if 0 <= discount <= 1:
            self.__discount = Decimal(str(discount))
            self._recalculate_total()
        else:
            raise ValueError("El descuento debe estar entre 0 y 1")
    
    # Métodos privados
    def _recalculate_total(self):
        """Recalcula el total cuando cambian cantidad o descuento"""
        # Nota: Esto requeriría el precio unitario del producto
        pass
    
    # Métodos de negocio
    def get_unit_price(self) -> Decimal:
        """Calcula el precio unitario antes del descuento"""
        if self.__quantity > 0:
            price_before_discount = self.__total_price / (1 - self.__discount)
            return price_before_discount / self.__quantity
        return Decimal('0')
    
    def get_discount_amount(self) -> Decimal:
        """Calcula el monto del descuento aplicado"""
        unit_price = self.get_unit_price()
        return unit_price * self.__quantity * self.__discount
    
    def get_profit_margin(self, cost_price: Decimal) -> Decimal:
        """Calcula el margen de ganancia"""
        unit_price = self.get_unit_price()
        profit = unit_price - cost_price
        return (profit / unit_price) * 100 if unit_price > 0 else Decimal('0')
    
    def is_bulk_sale(self, threshold: int = 10) -> bool:
        """Determina si es una venta al por mayor"""
        return self.__quantity >= threshold
    
    def is_discounted(self) -> bool:
        """Determina si la venta tiene descuento"""
        return self.__discount > 0
    
    def get_sale_details(self) -> dict:
        """Obtiene detalles completos de la venta con información relacionada"""
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
    
    @classmethod
    def find_by_id(cls, sales_id: int) -> Optional['Sale']:
        """Busca una venta por ID"""
        db = DatabaseConnection()
        query = "SELECT * FROM sales WHERE SalesID = %s"
        result = db.execute_query(query, (sales_id,))
        
        if result:
            row = result[0]
            return cls(
                row['SalesID'], row['SalesPersonID'], row['CustomerID'],
                row['ProductID'], row['Quantity'], float(row['Discount']),
                float(row['TotalPrice']), row['SalesDate'], row['TransactionNumber'],
                row['Customers_CustomerID'], row['Customers_cities_CityID'],
                row['Customers_cities_countries_CountryID']
            )
        return None
    
    @classmethod
    def get_by_date_range(cls, start_date: datetime, end_date: datetime) -> List['Sale']:
        """Obtiene ventas por rango de fechas"""
        db = DatabaseConnection()
        query = "SELECT * FROM sales WHERE SalesDate BETWEEN %s AND %s ORDER BY SalesDate"
        results = db.execute_query(query, (start_date, end_date))
        
        sales = []
        for row in results:
            sales.append(cls(
                row['SalesID'], row['SalesPersonID'], row['CustomerID'],
                row['ProductID'], row['Quantity'], float(row['Discount']),
                float(row['TotalPrice']), row['SalesDate'], row['TransactionNumber'],
                row['Customers_CustomerID'], row['Customers_cities_CityID'],
                row['Customers_cities_countries_CountryID']
            ))
        return sales
    
    @classmethod
    def get_sales_summary(cls, start_date: datetime = None, end_date: datetime = None) -> dict:
        """Obtiene resumen de ventas"""
        db = DatabaseConnection()
        
        if start_date and end_date:
            query = """
            SELECT 
                COUNT(SalesID) as total_sales,
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
            SELECT 
                COUNT(SalesID) as total_sales,
                SUM(TotalPrice) as total_revenue,
                AVG(TotalPrice) as avg_sale,
                SUM(Quantity) as total_units_sold,
                COUNT(DISTINCT CustomerID) as unique_customers
            FROM sales
            """
            result = db.execute_query(query)
        
        return result[0] if result else {}
    
    def save(self) -> int:
        """Guarda la venta en la base de datos"""
        db = DatabaseConnection()
        if self.__sales_id is None:
            query = """
            INSERT INTO sales (SalesPersonID, CustomerID, ProductID, Quantity, 
                             Discount, TotalPrice, SalesDate, TransactionNumber,
                             Customers_CustomerID, Customers_cities_CityID, 
                             Customers_cities_countries_CountryID) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            self.__sales_id = db.execute_insert(query, (
                self.__sales_person_id, self.__customer_id, self.__product_id,
                self.__quantity, float(self.__discount), float(self.__total_price),
                self.__sales_date, self.__transaction_number,
                self.__customers_customer_id, self.__customers_cities_city_id,
                self.__customers_cities_countries_country_id
            ))
        return self.__sales_id
    
    def __str__(self) -> str:
        return f"Venta #{self.__sales_id} - {self.__transaction_number} - ${self.__total_price:.2f}"
    
    def __repr__(self) -> str:
        return f"Sale(id={self.__sales_id}, customer_id={self.__customer_id}, total={self.__total_price})"
    
    def __eq__(self, other) -> bool:
        if isinstance(other, Sale):
            return self.__sales_id == other.__sales_id
        return False