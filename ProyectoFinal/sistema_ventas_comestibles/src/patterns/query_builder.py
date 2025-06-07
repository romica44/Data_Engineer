from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import pandas as pd
from src.database.connection import DatabaseConnection
import logging

class SQLQueryBuilder:
    """
    Builder Pattern para construir consultas SQL complejas de forma dinámica y legible.
    
    Patrón implementado: Builder
    Problema que resuelve:
    - Construcción compleja de consultas SQL con múltiples opciones
    - Permite crear consultas paso a paso de forma fluida (fluent interface)
    - Evita constructores con muchos parámetros
    - Facilita la reutilización y modificación de consultas
    - Mejora la legibilidad del código
    
    Beneficios:
    - Código más legible y mantenible
    - Flexibilidad para construir consultas complejas
    - Reutilización de componentes de consulta
    - Validación en cada paso de construcción
    """
    
    def __init__(self):
        """Inicializa el builder con valores por defecto"""
        self.reset()
        self.db = DatabaseConnection()
        self.logger = logging.getLogger(__name__)
    
    def reset(self) -> 'SQLQueryBuilder':
        """
        Reinicia el builder para construir una nueva consulta.
        
        Returns:
            SQLQueryBuilder: Self para method chaining
        """
        self._select_fields = []
        self._from_table = ""
        self._joins = []
        self._where_conditions = []
        self._group_by_fields = []
        self._having_conditions = []
        self._order_by_fields = []
        self._limit_value = None
        self._parameters = {}
        return self
    
    def select(self, *fields: str) -> 'SQLQueryBuilder':
        """
        Especifica los campos a seleccionar.
        
        Args:
            *fields: Campos a seleccionar en la consulta
            
        Returns:
            SQLQueryBuilder: Self para method chaining
        """
        self._select_fields.extend(fields)
        return self
    
    def select_with_alias(self, field: str, alias: str) -> 'SQLQueryBuilder':
        """
        Selecciona un campo con alias.
        
        Args:
            field (str): Campo original
            alias (str): Alias para el campo
            
        Returns:
            SQLQueryBuilder: Self para method chaining
        """
        self._select_fields.append(f"{field} as {alias}")
        return self
    
    def select_aggregate(self, function: str, field: str, alias: str = None) -> 'SQLQueryBuilder':
        """
        Selecciona un campo con función agregada.
        
        Args:
            function (str): Función agregada (COUNT, SUM, AVG, etc.)
            field (str): Campo a agregar
            alias (str, optional): Alias para el resultado
            
        Returns:
            SQLQueryBuilder: Self para method chaining
        """
        aggregate_field = f"{function}({field})"
        if alias:
            aggregate_field += f" as {alias}"
        
        self._select_fields.append(aggregate_field)
        return self
    
    def from_table(self, table: str) -> 'SQLQueryBuilder':
        """
        Especifica la tabla principal de la consulta.
        
        Args:
            table (str): Nombre de la tabla
            
        Returns:
            SQLQueryBuilder: Self para method chaining
        """
        self._from_table = table
        return self
    
    def join(self, table: str, condition: str, join_type: str = "JOIN") -> 'SQLQueryBuilder':
        """
        Agrega un JOIN a la consulta.
        
        Args:
            table (str): Tabla a unir
            condition (str): Condición del JOIN
            join_type (str): Tipo de JOIN (JOIN, LEFT JOIN, RIGHT JOIN, etc.)
            
        Returns:
            SQLQueryBuilder: Self para method chaining
        """
        self._joins.append(f"{join_type} {table} ON {condition}")
        return self
    
    def left_join(self, table: str, condition: str) -> 'SQLQueryBuilder':
        """
        Agrega un LEFT JOIN a la consulta.
        
        Args:
            table (str): Tabla a unir
            condition (str): Condición del JOIN
            
        Returns:
            SQLQueryBuilder: Self para method chaining
        """
        return self.join(table, condition, "LEFT JOIN")
    
    def inner_join(self, table: str, condition: str) -> 'SQLQueryBuilder':
        """
        Agrega un INNER JOIN a la consulta.
        
        Args:
            table (str): Tabla a unir
            condition (str): Condición del JOIN
            
        Returns:
            SQLQueryBuilder: Self para method chaining
        """
        return self.join(table, condition, "INNER JOIN")
    
    def where(self, condition: str, parameter_name: str = None, parameter_value: Any = None) -> 'SQLQueryBuilder':
        """
        Agrega una condición WHERE.
        
        Args:
            condition (str): Condición SQL
            parameter_name (str, optional): Nombre del parámetro
            parameter_value (Any, optional): Valor del parámetro
            
        Returns:
            SQLQueryBuilder: Self para method chaining
        """
        self._where_conditions.append(condition)
        
        if parameter_name and parameter_value is not None:
            self._parameters[parameter_name] = parameter_value
        
        return self
    
    def where_equals(self, field: str, value: Any) -> 'SQLQueryBuilder':
        """
        Agrega una condición WHERE de igualdad.
        
        Args:
            field (str): Campo a comparar
            value (Any): Valor a comparar
            
        Returns:
            SQLQueryBuilder: Self para method chaining
        """
        param_name = f"{field}_eq"
        condition = f"{field} = :{param_name}"
        return self.where(condition, param_name, value)
    
    def where_between(self, field: str, start_value: Any, end_value: Any) -> 'SQLQueryBuilder':
        """
        Agrega una condición WHERE BETWEEN.
        
        Args:
            field (str): Campo a comparar
            start_value (Any): Valor inicial
            end_value (Any): Valor final
            
        Returns:
            SQLQueryBuilder: Self para method chaining
        """
        start_param = f"{field}_start"
        end_param = f"{field}_end"
        condition = f"{field} BETWEEN :{start_param} AND :{end_param}"
        
        self._parameters[start_param] = start_value
        self._parameters[end_param] = end_value
        
        return self.where(condition)
    
    def where_in(self, field: str, values: List[Any]) -> 'SQLQueryBuilder':
        """
        Agrega una condición WHERE IN.
        
        Args:
            field (str): Campo a comparar
            values (List[Any]): Lista de valores
            
        Returns:
            SQLQueryBuilder: Self para method chaining
        """
        if not values:
            return self
        
        # Crear parámetros para cada valor
        param_names = []
        for i, value in enumerate(values):
            param_name = f"{field}_in_{i}"
            param_names.append(f":{param_name}")
            self._parameters[param_name] = value
        
        condition = f"{field} IN ({', '.join(param_names)})"
        return self.where(condition)
    
    def where_date_range(self, date_field: str, start_date: datetime = None, end_date: datetime = None) -> 'SQLQueryBuilder':
        """
        Agrega condiciones de rango de fechas.
        
        Args:
            date_field (str): Campo de fecha
            start_date (datetime, optional): Fecha inicial
            end_date (datetime, optional): Fecha final
            
        Returns:
            SQLQueryBuilder: Self para method chaining
        """
        if start_date and end_date:
            return self.where_between(date_field, start_date, end_date)
        elif start_date:
            param_name = f"{date_field}_start"
            condition = f"{date_field} >= :{param_name}"
            return self.where(condition, param_name, start_date)
        elif end_date:
            param_name = f"{date_field}_end"
            condition = f"{date_field} <= :{param_name}"
            return self.where(condition, param_name, end_date)
        
        return self
    
    def group_by(self, *fields: str) -> 'SQLQueryBuilder':
        """
        Agrega campos al GROUP BY.
        
        Args:
            *fields: Campos para agrupar
            
        Returns:
            SQLQueryBuilder: Self para method chaining
        """
        self._group_by_fields.extend(fields)
        return self
    
    def having(self, condition: str) -> 'SQLQueryBuilder':
        """
        Agrega una condición HAVING.
        
        Args:
            condition (str): Condición HAVING
            
        Returns:
            SQLQueryBuilder: Self para method chaining
        """
        self._having_conditions.append(condition)
        return self
    
    def order_by(self, field: str, direction: str = "ASC") -> 'SQLQueryBuilder':
        """
        Agrega un campo al ORDER BY.
        
        Args:
            field (str): Campo para ordenar
            direction (str): Dirección del ordenamiento (ASC o DESC)
            
        Returns:
            SQLQueryBuilder: Self para method chaining
        """
        self._order_by_fields.append(f"{field} {direction}")
        return self
    
    def order_by_desc(self, field: str) -> 'SQLQueryBuilder':
        """
        Agrega un campo al ORDER BY en orden descendente.
        
        Args:
            field (str): Campo para ordenar
            
        Returns:
            SQLQueryBuilder: Self para method chaining
        """
        return self.order_by(field, "DESC")
    
    def limit(self, count: int, offset: int = 0) -> 'SQLQueryBuilder':
        """
        Agrega LIMIT a la consulta.
        
        Args:
            count (int): Número de registros a limitar
            offset (int): Offset para paginación
            
        Returns:
            SQLQueryBuilder: Self para method chaining
        """
        if offset > 0:
            self._limit_value = f"LIMIT {offset}, {count}"
        else:
            self._limit_value = f"LIMIT {count}"
        return self
    
    def build(self) -> str:
        """
        Construye la consulta SQL final.
        
        Returns:
            str: Consulta SQL construida
            
        Raises:
            ValueError: Si la consulta no tiene los componentes mínimos necesarios
        """
        if not self._select_fields:
            raise ValueError("La consulta debe tener al menos un campo SELECT")
        
        if not self._from_table:
            raise ValueError("La consulta debe especificar una tabla FROM")
        
        # Construir la consulta paso a paso
        query_parts = []
        
        # SELECT
        select_clause = "SELECT " + ", ".join(self._select_fields)
        query_parts.append(select_clause)
        
        # FROM
        from_clause = f"FROM {self._from_table}"
        query_parts.append(from_clause)
        
        # JOINs
        if self._joins:
            query_parts.extend(self._joins)
        
        # WHERE
        if self._where_conditions:
            where_clause = "WHERE " + " AND ".join(self._where_conditions)
            query_parts.append(where_clause)
        
        # GROUP BY
        if self._group_by_fields:
            group_clause = "GROUP BY " + ", ".join(self._group_by_fields)
            query_parts.append(group_clause)
        
        # HAVING
        if self._having_conditions:
            having_clause = "HAVING " + " AND ".join(self._having_conditions)
            query_parts.append(having_clause)
        
        # ORDER BY
        if self._order_by_fields:
            order_clause = "ORDER BY " + ", ".join(self._order_by_fields)
            query_parts.append(order_clause)
        
        # LIMIT
        if self._limit_value:
            query_parts.append(self._limit_value)
        
        return "\n".join(query_parts)
    
    def execute(self) -> pd.DataFrame:
        """
        Ejecuta la consulta construida y retorna el resultado como DataFrame.
        
        Returns:
            pd.DataFrame: Resultado de la consulta
            
        Raises:
            Exception: Si hay error en la construcción o ejecución de la consulta
        """
        try:
            query = self.build()
            self.logger.info(f"🔨 Ejecutando consulta construida con Builder")
            self.logger.debug(f"Query: {query}")
            self.logger.debug(f"Parameters: {self._parameters}")
            
            result = self.db.execute_query_to_dataframe(query, self._parameters)
            
            self.logger.info(f"✅ Consulta ejecutada exitosamente. Filas: {len(result)}")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Error ejecutando consulta construida: {e}")
            raise
    
    def get_query_info(self) -> Dict[str, Any]:
        """
        Obtiene información sobre la consulta construida.
        
        Returns:
            dict: Información detallada de la consulta
        """
        try:
            query = self.build()
            return {
                'pattern_type': 'Builder',
                'query': query,
                'parameters': self._parameters.copy(),
                'components': {
                    'select_fields': len(self._select_fields),
                    'joins': len(self._joins),
                    'where_conditions': len(self._where_conditions),
                    'group_by_fields': len(self._group_by_fields),
                    'order_by_fields': len(self._order_by_fields),
                    'has_limit': self._limit_value is not None
                },
                'is_valid': True
            }
        except Exception as e:
            return {
                'pattern_type': 'Builder',
                'is_valid': False,
                'error': str(e),
                'components': {
                    'select_fields': len(self._select_fields),
                    'from_table': bool(self._from_table),
                    'joins': len(self._joins),
                    'where_conditions': len(self._where_conditions),
                    'group_by_fields': len(self._group_by_fields),
                    'order_by_fields': len(self._order_by_fields),
                    'has_limit': self._limit_value is not None
                }
            }

class SalesQueryBuilder(SQLQueryBuilder):
    """
    Builder especializado para consultas de ventas.
    Extiende SQLQueryBuilder con métodos específicos para análisis de ventas.
    """
    
    def __init__(self):
        super().__init__()
        # Configuración base para consultas de ventas
        self.from_table("sales s")
    
    def with_employee_info(self) -> 'SalesQueryBuilder':
        """
        Incluye información de empleados en la consulta.
        
        Returns:
            SalesQueryBuilder: Self para method chaining
        """
        return (self
                .inner_join("employees e", "s.SalesPersonID = e.EmployeeID")
                .select("CONCAT(e.FirstName, ' ', e.LastName) as employee_name"))
    
    def with_customer_info(self) -> 'SalesQueryBuilder':
        """
        Incluye información de clientes en la consulta.
        
        Returns:
            SalesQueryBuilder: Self para method chaining
        """
        return (self
                .inner_join("customers c", "s.CustomerID = c.CustomerID")
                .select("CONCAT(c.FirstName, ' ', c.LastName) as customer_name"))
    
    def with_product_info(self) -> 'SalesQueryBuilder':
        """
        Incluye información de productos en la consulta.
        
        Returns:
            SalesQueryBuilder: Self para method chaining
        """
        return (self
                .inner_join("products p", "s.ProductID = p.ProductID")
                .inner_join("categories cat", "p.CategoryID = cat.CategoryID")
                .select("p.ProductName", "cat.CategoryName", "p.Price as unit_price"))
    
    def with_geographic_info(self) -> 'SalesQueryBuilder':
        """
        Incluye información geográfica en la consulta.
        
        Returns:
            SalesQueryBuilder: Self para method chaining
        """
        return (self
                .inner_join("customers c", "s.CustomerID = c.CustomerID")
                .inner_join("cities ci", "c.CityID = ci.CityID")
                .inner_join("countries co", "ci.CountryID = co.CountryID")
                .select("ci.CityName", "co.CountryName"))
    
    def with_sales_metrics(self) -> 'SalesQueryBuilder':
        """
        Incluye métricas básicas de ventas.
        
        Returns:
            SalesQueryBuilder: Self para method chaining
        """
        return (self
                .select_aggregate("COUNT", "s.SalesID", "total_sales")
                .select_aggregate("SUM", "s.TotalPrice", "total_revenue")
                .select_aggregate("AVG", "s.TotalPrice", "avg_sale_amount")
                .select_aggregate("SUM", "s.Quantity", "total_units_sold"))
    
    def for_period(self, start_date: datetime = None, end_date: datetime = None) -> 'SalesQueryBuilder':
        """
        Filtra por período de fechas.
        
        Args:
            start_date (datetime, optional): Fecha de inicio
            end_date (datetime, optional): Fecha de fin
            
        Returns:
            SalesQueryBuilder: Self para method chaining
        """
        return self.where_date_range("s.SalesDate", start_date, end_date)
    
    def top_performers(self, limit: int = 10) -> 'SalesQueryBuilder':
        """
        Configura la consulta para obtener los mejores performers.
        
        Args:
            limit (int): Número de registros a retornar
            
        Returns:
            SalesQueryBuilder: Self para method chaining
        """
        return self.order_by_desc("total_revenue").limit(limit)

# Funciones de conveniencia
def create_sales_query() -> SalesQueryBuilder:
    """
    Función de conveniencia para crear un SalesQueryBuilder.
    
    Returns:
        SalesQueryBuilder: Nuevo builder para consultas de ventas
    """
    return SalesQueryBuilder()

def create_query() -> SQLQueryBuilder:
    """
    Función de conveniencia para crear un SQLQueryBuilder general.
    
    Returns:
        SQLQueryBuilder: Nuevo builder para consultas SQL
    """
    return SQLQueryBuilder()