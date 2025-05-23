-- Crear base de datos
CREATE DATABASE IF NOT EXISTS grocery_sales_db;
USE grocery_sales_db;

-- Crear tabla countries
CREATE TABLE IF NOT EXISTS countries (
    CountryID INT PRIMARY KEY AUTO_INCREMENT,
    CountryName VARCHAR(45) NOT NULL,
    CountryCode VARCHAR(2) NOT NULL
);

-- Crear tabla cities
CREATE TABLE IF NOT EXISTS cities (
    CityID INT PRIMARY KEY AUTO_INCREMENT,
    CityName VARCHAR(45) NOT NULL,
    Zipcode DECIMAL(5,0),
    CountryID INT NOT NULL,
    countries_CountryID INT NOT NULL,
    FOREIGN KEY (CountryID) REFERENCES countries(CountryID),
    FOREIGN KEY (countries_CountryID) REFERENCES countries(CountryID)
);

-- Crear tabla categories
CREATE TABLE IF NOT EXISTS categories (
    CategoryID INT PRIMARY KEY AUTO_INCREMENT,
    CategoryName VARCHAR(45) NOT NULL
);

-- Crear tabla products
CREATE TABLE IF NOT EXISTS products (
    ProductID INT PRIMARY KEY AUTO_INCREMENT,
    ProductName VARCHAR(45) NOT NULL,
    Price DECIMAL(10,2) NOT NULL,
    CategoryID INT NOT NULL,
    Class VARCHAR(45),
    ModifyDate DATE,
    Resistant VARCHAR(45),
    JuMiergc VARCHAR(10),
    VariableDate DECIMAL(3,0),
    FOREIGN KEY (CategoryID) REFERENCES categories(CategoryID)
);

-- Crear tabla customers
CREATE TABLE IF NOT EXISTS customers (
    CustomerID INT PRIMARY KEY AUTO_INCREMENT,
    FirstName VARCHAR(45) NOT NULL,
    MiddleInitial VARCHAR(1),
    LastName VARCHAR(45) NOT NULL,
    CityID INT NOT NULL,
    Address VARCHAR(90),
    cities_CityID INT NOT NULL,
    cities_countries_CountryID INT NOT NULL,
    FOREIGN KEY (CityID) REFERENCES cities(CityID),
    FOREIGN KEY (cities_CityID) REFERENCES cities(CityID),
    FOREIGN KEY (cities_countries_CountryID) REFERENCES countries(CountryID)
);

-- Crear tabla employees
CREATE TABLE IF NOT EXISTS employees (
    EmployeeID INT PRIMARY KEY AUTO_INCREMENT,
    FirstName VARCHAR(45) NOT NULL,
    MiddleInitial VARCHAR(1),
    LastName VARCHAR(45) NOT NULL,
    BirthDate DATE,
    Gender VARCHAR(1),
    CityID INT NOT NULL,
    HireDate DATE,
    sales_SalesID INT,
    sales_customers_CustomerID INT,
    sales_customers_cities_CityID INT,
    sales_customers_cities_countries_CountryID INT,
    FOREIGN KEY (CityID) REFERENCES cities(CityID)
);

-- Crear tabla sales
CREATE TABLE IF NOT EXISTS sales (
    SalesID INT PRIMARY KEY AUTO_INCREMENT,
    SalesPersonID INT NOT NULL,
    CustomerID INT NOT NULL,
    ProductID INT NOT NULL,
    Quantity INT NOT NULL,
    Discount DECIMAL(10,2) DEFAULT 0.00,
    TotalPrice DECIMAL(10,2) NOT NULL,
    SalesDate DATETIME NOT NULL,
    TransactionNumber VARCHAR(255),
    Customers_CustomerID INT NOT NULL,
    Customers_cities_CityID INT NOT NULL,
    Customers_cities_countries_CountryID INT NOT NULL,
    FOREIGN KEY (SalesPersonID) REFERENCES employees(EmployeeID),
    FOREIGN KEY (CustomerID) REFERENCES customers(CustomerID),
    FOREIGN KEY (ProductID) REFERENCES products(ProductID),
    FOREIGN KEY (Customers_CustomerID) REFERENCES customers(CustomerID),
    FOREIGN KEY (Customers_cities_CityID) REFERENCES cities(CityID),
    FOREIGN KEY (Customers_cities_countries_CountryID) REFERENCES countries(CountryID)
);

-- Crear índices para mejorar performance
CREATE INDEX idx_sales_date ON sales(SalesDate);
CREATE INDEX idx_sales_customer ON sales(CustomerID);
CREATE INDEX idx_sales_product ON sales(ProductID);
CREATE INDEX idx_sales_transaction ON sales(TransactionNumber);
CREATE INDEX idx_customer_city ON customers(CityID);
CREATE INDEX idx_product_category ON products(CategoryID);