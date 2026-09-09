"""
Punto de entrada del sistema: muestra un menú por consola y llama
a los métodos de la clase Biblioteca según lo que elija la persona.
"""

from biblioteca import Biblioteca

OPCIONES = """
========= Sistema de Biblioteca =========
1. Añadir libro / inventario nuevo
2. Consultar catálogo (título y/o autor)
3. Registrar usuario(a)
4. Salir
===========================================
"""


def pedir_libro_y_agregar(biblioteca: Biblioteca) -> None:
    print("\n-- Añadir libro --")
    isbn = input("ISBN: ").strip()
    titulo = input("Título: ").strip()
    apellido_autor = input("Apellido del autor: ").strip()
    nombre_autor = input("Nombre del autor: ").strip()
    fecha_nac = input("Fecha de nacimiento del autor (YYYY-MM-DD, opcional): ").strip() or None

    try:
        anio = int(input("Año de publicación: ").strip())
        cantidad = int(input("Cantidad de copias: ").strip())
    except ValueError:
        print("El año y la cantidad deben ser números enteros.")
        return

    try:
        biblioteca.agregar_libro(
            isbn=isbn,
            titulo=titulo,
            anio_publicacion=anio,
            cantidad_nueva=cantidad,
            autor_nombre=nombre_autor,
            autor_apellido=apellido_autor,
            autor_fecha_nacimiento=fecha_nac,
        )
    except ValueError as error:
        print(f"No se pudo registrar el libro: {error}")


def pedir_busqueda(biblioteca: Biblioteca) -> None:
    print("\n-- Consultar catálogo --")
    termino = input("Título o autor a buscar: ").strip()
    biblioteca.buscar_catalogo(termino)


def pedir_usuario_y_crear(biblioteca: Biblioteca) -> None:
    print("\n-- Registrar usuario --")
    dni = input("DNI (8 dígitos): ").strip()
    nombre = input("Nombre: ").strip()
    apellido = input("Apellido: ").strip()
    email = input("Email: ").strip()
    telefono = input("Teléfono (opcional): ").strip() or None

    try:
        biblioteca.crear_usuario(dni, nombre, apellido, email, telefono)
    except ValueError as error:
        print(f"No se pudo registrar el usuario: {error}")


def main() -> None:
    biblioteca = Biblioteca("biblioteca.db")
    biblioteca.crear_tablas()

    acciones = {
        "1": pedir_libro_y_agregar,
        "2": pedir_busqueda,
        "3": pedir_usuario_y_crear,
    }

    while True:
        print(OPCIONES)
        opcion = input("Elige una opción: ").strip()

        if opcion == "4":
            print("Sesión terminada.")
            break
        elif opcion in acciones:
            acciones[opcion](biblioteca)
        else:
            print("Opción no válida.")

    biblioteca.cerrar()


if __name__ == "__main__":
    main()
