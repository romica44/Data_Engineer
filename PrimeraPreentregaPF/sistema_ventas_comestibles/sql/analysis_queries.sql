USE grocery_sales_db;

-- Consultas de análisis para el sistema de ventas

-- 1. Ventas por categoría de producto
SELECT 
    c.CategoryName,
    COUNT(s.SalesID) as TotalVentas,
    SUM(s.TotalPrice) as IngresoTotal,
    AVG(s.TotalPrice) as PromedioVenta
FROM sales s
JOIN products p ON s.ProductID = p.ProductID
JOIN categories c ON p.CategoryID = c.CategoryID
GROUP BY c.CategoryID, c.CategoryName
ORDER BY IngresoTotal DESC;

-- 2. Rendimiento de empleados
SELECT 
    e.EmployeeID,
    CONCAT(e.FirstName, ' ', e.LastName) as NombreCompleto,
    COUNT(s.SalesID) as VentasRealizadas,
    SUM(s.TotalPrice) as IngresoGenerado,
    AVG(s.TotalPrice) as PromedioVenta
FROM employees e
JOIN sales s ON e.EmployeeID = s.SalesPersonID
GROUP BY e.EmployeeID
ORDER BY IngresoGenerado DESC;

-- 3. Análisis geográfico de ventas
SELECT 
    co.CountryName,
    ci.CityName,
    COUNT(s.SalesID) as TotalVentas,
    SUM(s.TotalPrice) as IngresoTotal
FROM sales s
JOIN customers cu ON s.CustomerID = cu.CustomerID
JOIN cities ci ON cu.CityID = ci.CityID
JOIN countries co ON ci.CountryID = co.CountryID
GROUP BY co.CountryID, ci.CityID
ORDER BY co.CountryName, IngresoTotal DESC;

-- 4. Productos más vendidos
SELECT 
    p.ProductName,
    c.CategoryName,
    SUM(s.Quantity) as UnidadesVendidas,
    SUM(s.TotalPrice) as IngresoTotal,
    COUNT(DISTINCT s.CustomerID) as ClientesUnicos
FROM sales s
JOIN products p ON s.ProductID = p.ProductID
JOIN categories c ON p.CategoryID = c.CategoryID
GROUP BY p.ProductID
ORDER BY UnidadesVendidas DESC
LIMIT 10;

-- 5. Clientes más valiosos
SELECT 
    CONCAT(cu.FirstName, ' ', cu.LastName) as NombreCompleto,
    ci.CityName,
    co.CountryName,
    COUNT(s.SalesID) as TotalCompras,
    SUM(s.TotalPrice) as GastoTotal,
    AVG(s.TotalPrice) as PromedioCompra
FROM customers cu
JOIN sales s ON cu.CustomerID = s.CustomerID
JOIN cities ci ON cu.CityID = ci.CityID
JOIN countries co ON ci.CountryID = co.CountryID
GROUP BY cu.CustomerID
ORDER BY GastoTotal DESC
LIMIT 10;

-- 6. Análisis temporal de ventas
SELECT 
    DATE(s.SalesDate) as Fecha,
    COUNT(s.SalesID) as VentasDelDia,
    SUM(s.TotalPrice) as IngresoDelDia,
    AVG(s.TotalPrice) as PromedioVenta
FROM sales s
GROUP BY DATE(s.SalesDate)
ORDER BY Fecha;

-- 7. Efectividad de descuentos
SELECT 
    CASE 
        WHEN s.Discount = 0 THEN 'Sin Descuento'
        WHEN s.Discount <= 0.10 THEN '1-10%'
        WHEN s.Discount <= 0.20 THEN '11-20%'
        ELSE 'Más de 20%'
    END as RangoDescuento,
    COUNT(s.SalesID) as NumeroVentas,
    AVG(s.TotalPrice) as PromedioVenta,
    SUM(s.TotalPrice) as IngresoTotal
FROM sales s
GROUP BY RangoDescuento
ORDER BY IngresoTotal DESC;