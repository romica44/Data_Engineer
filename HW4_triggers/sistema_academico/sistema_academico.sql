
-- Crear base de datos si no existe
CREATE DATABASE IF NOT EXISTS sistema_academico;
USE sistema_academico;

-- Crear tablas principales
CREATE TABLE IF NOT EXISTS estudiantes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100),
    email VARCHAR(100),
    estado VARCHAR(20) DEFAULT 'activo'
);

CREATE TABLE IF NOT EXISTS materias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100),
    creditos INT
);

CREATE TABLE IF NOT EXISTS inscripciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    estudiante_id INT,
    materia_id INT,
    fecha DATE,
    FOREIGN KEY (estudiante_id) REFERENCES estudiantes(id),
    FOREIGN KEY (materia_id) REFERENCES materias(id)
);

CREATE TABLE IF NOT EXISTS calificaciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    estudiante_id INT,
    materia_id INT,
    nota DECIMAL(4,2),
    fecha DATE,
    FOREIGN KEY (estudiante_id) REFERENCES estudiantes(id),
    FOREIGN KEY (materia_id) REFERENCES materias(id)
);

CREATE TABLE IF NOT EXISTS auditoria_eliminaciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    estudiante_id INT,
    email VARCHAR(255),
    eliminado_en DATETIME
);

-- Crear funciones
DROP FUNCTION IF EXISTS promedio_estudiante;
DROP FUNCTION IF EXISTS estado_academico;

DELIMITER $$

CREATE FUNCTION promedio_estudiante(est_id INT)
RETURNS DECIMAL(4,2)
DETERMINISTIC
BEGIN
    DECLARE promedio DECIMAL(4,2);
    SELECT AVG(nota) INTO promedio
    FROM calificaciones
    WHERE estudiante_id = est_id;
    RETURN promedio;
END$$

CREATE FUNCTION estado_academico(est_id INT)
RETURNS VARCHAR(20)
DETERMINISTIC
BEGIN
    DECLARE promedio DECIMAL(4,2);
    SET promedio = promedio_estudiante(est_id);

    IF promedio >= 6 THEN
        RETURN 'Aprobado';
    ELSE
        RETURN 'Desaprobado';
    END IF;
END$$

-- Crear vistas
DROP VIEW IF EXISTS rendimiento_estudiantes;
DROP VIEW IF EXISTS promedio_materias;

CREATE VIEW rendimiento_estudiantes AS
SELECT 
    e.id AS estudiante_id,
    e.nombre,
    promedio_estudiante(e.id) AS promedio,
    estado_academico(e.id) AS estado
FROM estudiantes e;

CREATE VIEW promedio_materias AS
SELECT 
    m.id AS materia_id,
    m.nombre,
    AVG(c.nota) AS promedio_general
FROM materias m
JOIN calificaciones c ON m.id = c.materia_id
GROUP BY m.id, m.nombre;

DELIMITER ;
