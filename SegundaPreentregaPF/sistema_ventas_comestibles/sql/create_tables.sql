
-- Crear base de datos
CREATE DATABASE IF NOT EXISTS grocery_sales_db;
USE grocery_sales_db;

-- Crear tabla countries
CREATE TABLE IF NOT EXISTS countries (
    CountryID INT PRIMARY KEY AUTO_INCREMENT,
    CountryName VARCHAR(100) NOT NULL,
    CountryCode VARCHAR(10) NOT NULL
);

-- Crear tabla cities
CREATE TABLE IF NOT EXISTS cities (
    CityID INT PRIMARY KEY AUTO_INCREMENT,
    CityName VARCHAR(100) NOT NULL,
    Zipcode VARCHAR(10),
    CountryID INT NOT NULL,
    FOREIGN KEY (CountryID) REFERENCES countries(CountryID)
);

-- Crear tabla categories
CREATE TABLE IF NOT EXISTS categories (
    CategoryID INT PRIMARY KEY AUTO_INCREMENT,
    CategoryName VARCHAR(100) NOT NULL
);

-- Crear tabla products
CREATE TABLE IF NOT EXISTS products (
    ProductID INT PRIMARY KEY AUTO_INCREMENT,
    ProductName VARCHAR(100) NOT NULL,
    Price DECIMAL(10,2) NOT NULL,
    CategoryID INT NOT NULL,
    Class VARCHAR(50),
    ModifyDate DATE,
    Resistant BOOLEAN,
    IsAllergic BOOLEAN,
    VitalityDays INT,
    FOREIGN KEY (CategoryID) REFERENCES categories(CategoryID)
);

-- Crear tabla customers
CREATE TABLE IF NOT EXISTS customers (
    CustomerID INT PRIMARY KEY AUTO_INCREMENT,
    FirstName VARCHAR(50) NOT NULL,
    MiddleInitial CHAR(1),
    LastName VARCHAR(50) NOT NULL,
    CityID INT NOT NULL,
    Address VARCHAR(100),
    FOREIGN KEY (CityID) REFERENCES cities(CityID)
);

-- Crear tabla employees
CREATE TABLE IF NOT EXISTS employees (
    EmployeeID INT PRIMARY KEY AUTO_INCREMENT,
    FirstName VARCHAR(50) NOT NULL,
    MiddleInitial CHAR(1),
    LastName VARCHAR(50) NOT NULL,
    BirthDate DATE,
    Gender ENUM('M', 'F'),
    CityID INT NOT NULL,
    HireDate DATE,
    FOREIGN KEY (CityID) REFERENCES cities(CityID)
);

-- Crear tabla sales
CREATE TABLE IF NOT EXISTS sales (
    SalesID INT PRIMARY KEY AUTO_INCREMENT,
    SalesPersonID INT NOT NULL,
    CustomerID INT NOT NULL,
    ProductID INT NOT NULL,
    Quantity INT NOT NULL,
    Discount DECIMAL(5,2) DEFAULT 0.00,
    TotalPrice DECIMAL(10,2) NOT NULL,
    SalesDate DATE NOT NULL,
    TransactionNumber VARCHAR(50),
    FOREIGN KEY (SalesPersonID) REFERENCES employees(EmployeeID),
    FOREIGN KEY (CustomerID) REFERENCES customers(CustomerID),
    FOREIGN KEY (ProductID) REFERENCES products(ProductID)
);

-- Crear índices para mejorar performance
CREATE INDEX idx_sales_date ON sales(SalesDate);
CREATE INDEX idx_sales_customer ON sales(CustomerID);
CREATE INDEX idx_sales_product ON sales(ProductID);
CREATE INDEX idx_sales_transaction ON sales(TransactionNumber);
CREATE INDEX idx_customer_city ON customers(CityID);
CREATE INDEX idx_product_category ON products(CategoryID);