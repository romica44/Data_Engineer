USE grocery_sales_db;

-- Deshabilitar verificaciones de claves foráneas temporalmente
SET FOREIGN_KEY_CHECKS = 0;

-- Limpiar tablas existentes
TRUNCATE TABLE sales;
TRUNCATE TABLE employees;
TRUNCATE TABLE customers;
TRUNCATE TABLE products;
TRUNCATE TABLE categories;
TRUNCATE TABLE cities;
TRUNCATE TABLE countries;

-- Cargar datos desde archivos CSV

LOAD DATA INFILE 'C:/Users/Home/Desktop/Data_Engineer/PrimeraPreentregaPF/sistema_ventas_comestibles/data/countries.csv'
INTO TABLE countries
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(CountryID, CountryName, CountryCode);

LOAD DATA INFILE 'C:/Users/Home/Desktop/Data_Engineer/PrimeraPreentregaPF/sistema_ventas_comestibles/data/cities.csv'
INTO TABLE cities
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(CityID, CityName, Zipcode, CountryID, CountryID);

LOAD DATA INFILE 'C:/Users/Home/Desktop/Data_Engineer/PrimeraPreentregaPF/sistema_ventas_comestibles/data/categories.csv'
INTO TABLE categories
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(CategoryID, CategoryName);

LOAD DATA INFILE 'C:/Users/Home/Desktop/Data_Engineer/PrimeraPreentregaPF/sistema_ventas_comestibles/data/products.csv'
INTO TABLE products
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(ProductID, ProductName, Price, CategoryID, Class, ModifyDate, Resistant, JuMiergc, VariableDate);

LOAD DATA INFILE 'C:/Users/Home/Desktop/Data_Engineer/PrimeraPreentregaPF/sistema_ventas_comestibles/data/customers.csv'
INTO TABLE customers
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(CustomerID, FirstName, MiddleInitial, LastName, CityID, Address);

LOAD DATA INFILE 'C:/Users/Home/Desktop/Data_Engineer/PrimeraPreentregaPF/sistema_ventas_comestibles/data/employees.csv'
INTO TABLE employees
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(EmployeeID, FirstName, MiddleInitial, LastName, BirthDate, Gender, CityID, HireDate)
SET 
    sales_SalesID = NULLIF(@sales_SalesID, ''),
    sales_customers_CustomerID = NULLIF(@sales_customers_CustomerID, ''),
    sales_customers_cities_CityID = NULLIF(@sales_customers_cities_CityID, ''),
    sales_customers_cities_countries_CountryID = NULLIF(@sales_customers_cities_countries_CountryID, '');

LOAD DATA INFILE 'C:/Users/Home/Desktop/Data_Engineer/PrimeraPreentregaPF/sistema_ventas_comestibles/data/sales.csv'
INTO TABLE sales
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(SalesID, SalesPersonID, CustomerID, ProductID, Quantity, Discount, TotalPrice, SalesDate, TransactionNumber);

-- Rehabilitar verificaciones de claves foráneas
SET FOREIGN_KEY_CHECKS = 1;

-- Verificar datos cargados
SELECT 'Countries' as tabla, COUNT(*) as registros FROM countries
UNION ALL
SELECT 'Cities' as tabla, COUNT(*) as registros FROM cities
UNION ALL
SELECT 'Categories' as tabla, COUNT(*) as registros FROM categories
UNION ALL
SELECT 'Products' as tabla, COUNT(*) as registros FROM products
UNION ALL
SELECT 'Customers' as tabla, COUNT(*) as registros FROM customers
UNION ALL
SELECT 'Employees' as tabla, COUNT(*) as registros FROM employees
UNION ALL
SELECT 'Sales' as tabla, COUNT(*) as registros FROM sales;