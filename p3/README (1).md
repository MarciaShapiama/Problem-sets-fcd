<div align="right">
  <img src="assets/inei_logo.png" width="130" alt="Logo INEI">
</div>

# Biblioteca — Sistema de Gestión de Libros y Usuarios

**Curso:** Fundamentos de Ciencia de Datos
**Docente:** Carla Solis Uehara
**Alumna:** Marcia Shapiama De La Cruz
**Fecha:** Setiembre 2026

---

## Índice

1. [Introducción](#introducción)
2. [Estructura del proyecto](#estructura-del-proyecto)
3. [Cómo funciona](#cómo-funciona)
4. [Añadir libros e inventario](#1-añadir-libros-e-inventario)
5. [Consultar el catálogo](#2-consultar-el-catálogo)
6. [Crear usuarios](#3-crear-usuarios)
7. [Administrar préstamos](#4-administrar-préstamos-diseño-no-implementado)
8. [Cómo usarlo](#cómo-usarlo)

---

## Introducción

Sistema de biblioteca en Python y SQLite, basado en el modelo relacional entregado en la Parte 1 de este Problem Set. Registra autores, libros y usuarios, y se maneja completamente por consola.

## Estructura del proyecto

```text
Problem Set 3/
│
├── biblioteca.db     <- se genera solo al ejecutar el programa
├── biblioteca.py      <- clase Biblioteca: conexión, esquema y lógica
├── menu.py             <- menú interactivo, punto de entrada
├── test_ps3.py          <- pruebas usadas durante el desarrollo
└── README.md
```

| Archivo | Para qué sirve |
|---|---|
| `biblioteca.db` | Base de datos SQLite donde quedan guardados autores, libros y usuarios. |
| `biblioteca.py` | Define la clase `Biblioteca`: abre la conexión, crea las tablas y la vista, y tiene un método por cada operación (agregar libro, buscar en el catálogo, crear usuario). |
| `menu.py` | Programa principal. Muestra el menú, pide los datos por teclado y llama a los métodos de `Biblioteca`. |
| `test_ps3.py` | Script de pruebas para verificar que cada caso (ISBN repetido, DNI inválido, año futuro, etc.) se comporta como debería. |

## Cómo funciona

`menu.py` no habla con la base de datos directamente: crea una instancia de `Biblioteca` y le pide que ejecute cada operación. Toda la conexión, el esquema y las reglas de negocio quedan dentro de esa clase, en `biblioteca.py`.

```text
menu.py  --pide datos y llama-->  Biblioteca (biblioteca.py)  --lee/escribe-->  biblioteca.db
```

## 1. Añadir libros e inventario

`agregar_libro` registra un libro nuevo (ISBN, título, año, cantidad, autor). Si el ISBN ya existe, solo suma copias al stock. Si el autor ya está registrado (ignorando tildes y mayúsculas), no lo duplica: se usa una columna `nombre_normalizado` en la tabla `Autor`, con restricción `UNIQUE`.

También valida que el año de publicación no sea futuro. Esto se hace en Python antes del INSERT, no con un trigger.

## 2. Consultar el catálogo

`buscar_catalogo` busca por título o autor sobre `CatalogoView` (une `Libro` y `Autor`), ignorando tildes y mayúsculas. Muestra título, autor y cantidad disponible.

## 3. Crear usuarios

`crear_usuario` registra DNI, nombre, apellido, email y teléfono opcional. El DNI se valida como 8 dígitos numéricos, primero con una expresión regular en Python y luego con un `CHECK` en la tabla. El `UNIQUE` en DNI evita duplicados.

## 4. Administrar préstamos (diseño, no implementado)

Tabla que haría falta:

```text
Prestamo(
    IDPrestamo        PK,
    IDUsuario         FK -> Usuario,
    IDLibro           FK -> Libro,
    fecha_prestamo    DATE,
    fecha_devolucion  DATE NULL   -- NULL = préstamo activo
)
```

Reglas a validar antes de prestar: que `cantidad_disponible > 0`, y que el usuario tenga menos de 3 préstamos activos (contando `Prestamo` con `fecha_devolucion IS NULL`); esto último se podría reforzar con un trigger `BEFORE INSERT`. Al prestar se descuenta 1 de `cantidad_disponible`, y al devolver se vuelve a sumar.

Hace falta una transacción porque verificar disponibilidad, insertar el préstamo y actualizar el stock deben ocurrir juntos: sin ella, dos usuarios podrían pedir el último ejemplar casi al mismo tiempo y ambos verían stock disponible antes de que se registre el descuento.

```sql
BEGIN TRANSACTION;
  -- 1. Verificar cantidad_disponible > 0
  -- 2. Verificar que el usuario tenga menos de 3 préstamos activos
  -- 3. INSERT INTO Prestamo (...)
  -- 4. UPDATE Libro SET cantidad_disponible = cantidad_disponible - 1 ...
COMMIT;  -- o ROLLBACK si algo falla
```

## Cómo usarlo

```bash
python menu.py
```

Crea la base de datos automáticamente y muestra:

```text
1. Añadir libro / inventario nuevo
2. Consultar catálogo (por título y/o autor)
3. Crear usuario(a)
4. Salir
```
