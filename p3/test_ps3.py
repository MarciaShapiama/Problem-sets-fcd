import os
from datetime import date
import sqlite3

if os.path.exists("biblioteca.db"):
    os.remove("biblioteca.db")

from biblioteca import Biblioteca

b = Biblioteca("biblioteca.db")
b.crear_tablas()

def check(desc, cond):
    print(f"[{'OK' if cond else 'FALLA'}] {desc}")

print("\n=== TEST 1: Libro nuevo (autor nuevo) ===")
b.agregar_libro("978-1", "Cien años de soledad", 1967, 3, "Gabriel", "García Márquez", "1927-03-06")
cur = b.conexion.execute("SELECT cantidad_disponible FROM Libro WHERE ISBN='978-1'")
check("cantidad = 3", cur.fetchone()["cantidad_disponible"] == 3)

print("\n=== TEST 2: mismo ISBN -> solo suma copias ===")
b.agregar_libro("978-1", "Cien años de soledad", 1967, 2, "Gabriel", "García Márquez")
cur = b.conexion.execute("SELECT cantidad_disponible FROM Libro WHERE ISBN='978-1'")
check("cantidad = 5", cur.fetchone()["cantidad_disponible"] == 5)
n_autores = b.conexion.execute("SELECT COUNT(*) c FROM Autor").fetchone()["c"]
check("sigue 1 solo autor", n_autores == 1)

print("\n=== TEST 3: autor existente escrito distinto (tildes/mayúsculas) ===")
b.agregar_libro("978-2", "El amor en los tiempos del cólera", 1985, 1, "GABRIEL", "garcia marquez")
n_autores = b.conexion.execute("SELECT COUNT(*) c FROM Autor").fetchone()["c"]
check("no se duplicó el autor", n_autores == 1)

print("\n=== TEST 4: año futuro -> debe rechazar SIN guardar autor a medias ===")
try:
    b.agregar_libro("978-3", "Libro futuro", date.today().year + 5, 1, "Autor", "Futurista")
    check("rechazó año futuro", False)
except ValueError:
    check("rechazó año futuro", True)
n_autores = b.conexion.execute("SELECT COUNT(*) c FROM Autor").fetchone()["c"]
check("NO quedó 'Autor Futurista' guardado a medias", n_autores == 1)

print("\n=== TEST 5: cantidad 0 -> debe rechazar ===")
try:
    b.agregar_libro("978-4", "X", 2000, 0, "A", "B")
    check("rechazó cantidad 0", False)
except ValueError:
    check("rechazó cantidad 0", True)

print("\n=== TEST 6: búsqueda por autor sin tilde ===")
r = b.buscar_catalogo("garcia")
check("2 resultados", len(r) == 2)

print("\n=== TEST 7: búsqueda por título parcial ===")
r = b.buscar_catalogo("cien")
check("1 resultado", len(r) == 1)

print("\n=== TEST 8: búsqueda sin resultados ===")
r = b.buscar_catalogo("no_existe_xyz")
check("lista vacía, no crashea", r == [])

print("\n=== TEST 9: crear usuario válido ===")
uid = b.crear_usuario("12345678", "Marci", "Shapiama", "marci@esan.pe", "999999999")
check("usuario creado", uid is not None)

print("\n=== TEST 10: DNI duplicado ===")
uid2 = b.crear_usuario("12345678", "Otra", "Persona", "otra@esan.pe")
check("rechaza sin crashear", uid2 is None)

print("\n=== TEST 11: DNI con letras ===")
try:
    b.crear_usuario("1234567A", "X", "Y", "x@x.com")
    check("rechazó", False)
except ValueError:
    check("rechazó", True)

print("\n=== TEST 12: borrar autor con libros -> debe fallar (RESTRICT) ===")
autor_id = b.conexion.execute("SELECT IDAutor FROM Autor LIMIT 1").fetchone()["IDAutor"]
try:
    b.conexion.execute("DELETE FROM Autor WHERE IDAutor=?", (autor_id,))
    b.conexion.commit()
    check("bloqueó borrado", False)
except sqlite3.IntegrityError:
    check("bloqueó borrado (RESTRICT funciona)", True)

b.cerrar()
print("\n=== FIN ===")
