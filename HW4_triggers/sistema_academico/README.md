# Sistema Académico - Base de Datos

Este proyecto implementa una base de datos académica completa en MySQL. Está diseñada para registrar estudiantes, materias, calificaciones, inscripciones, y realizar análisis a través de funciones, procedimientos almacenados, triggers y vistas.

---

## 📂 Archivo principal

- `sistema_academico_actualizado.sql`  
  Contiene todo el esquema de base de datos necesario:
  - Creación de la base de datos
  - Tablas principales
  - Funciones
  - Triggers
  - Procedimientos almacenados
  - Vistas para análisis académico

---

## 🧱 Estructura de la base de datos

### Tablas
- `estudiantes`: información personal y estado académico del estudiante
- `materias`: materias disponibles en la institución
- `inscripciones`: relación estudiante-materia con fecha
- `calificaciones`: notas de estudiantes por materia
- `auditoria_eliminaciones`: registros de auditoría al eliminar estudiantes

---

## ⚙️ Funciones

- `promedio_estudiante(est_id)`  
  Calcula el promedio general de calificaciones de un estudiante.

- `estado_academico(est_id)`  
  Devuelve 'Aprobado' si el promedio es igual o mayor a 6, o 'Desaprobado' en caso contrario.

---

## 🔁 Triggers

- `before_delete_estudiante`  
  Guarda automáticamente en la tabla `auditoria_eliminaciones` los datos del estudiante antes de eliminarlo.

- `after_insert_calificacion`  
  Calcula el nuevo promedio del estudiante y actualiza su estado (`aprobado` o `desaprobado`) automáticamente.

---

## 🧪 Procedimientos

- `registrar_calificacion(estudiante_id, materia_id, nota, fecha)`  
  Registra una calificación, validando que la nota esté entre 0 y 10.

- `inscribir_estudiante(estudiante_id, materia_id, fecha)`  
  Inscribe un estudiante solo si su estado actual es "activo".

---

## 👁️ Vistas

- `rendimiento_estudiantes`: muestra el nombre, promedio y estado académico de cada estudiante.
- `promedio_materias`: muestra el promedio general de calificaciones por materia.

---

## 🚀 Cómo usar

1. Abrí tu cliente de MySQL (phpMyAdmin, MySQL Workbench, consola).
2. Importá el archivo `sistema_academico_actualizado.sql`.
3. Las tablas, funciones, triggers, procedimientos y vistas quedarán listas para usar.

---

## 📝 Licencia

Este proyecto está bajo licencia MIT. Ver archivo `LICENSE`.

---

## 👩‍💻 Autora

**Romina Cattaneo**  
Data Engineer  
📧 romica44@gmail.com  
🔗 [LinkedIn](https://www.linkedin.com/in/romina-paola-cattaneo-9757b345/)

### 🏆 **Segunda Entrega - Patrones de Diseño**
- ✅ **4 patrones de diseño** implementados y justificados
- ✅ **SQLAlchemy + Singleton** para conexión robusta
- ✅ **Pandas DataFrames** como formato estándar
- ✅ **Pruebas unitarias** completas con pytest
- ✅ **Jupyter Notebook** demostrativo
- ✅ **Arquitectura empresarial** escalable y mantenible

---
