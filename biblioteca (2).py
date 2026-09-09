"""
Sistema de gestión de biblioteca (Problem Set 3, Parte 2).

La clase Biblioteca junta en un solo objeto la conexión a SQLite y
las operaciones que pide el enunciado: registrar libros, consultar
el catálogo y crear usuarios.

Se optó por una sola clase en vez de dividir el proyecto en archivos
por capa (conexión, lógica, menú). Para el tamaño de este sistema es
más directo tener un objeto Biblioteca con un método por cada
requisito, y así el menú solo tiene que llamarlos sin preocuparse de
cómo están implementados por dentro.
"""

import sqlite3
from datetime import date
from typing import Optional


class Biblioteca:
    """
    Representa el sistema de biblioteca y su conexión a la base de
    datos. Cada instancia abre su propia conexión al archivo SQLite
    indicado en db_path.
    """

    def __init__(self, db_path: str = "biblioteca.db"):
        self.db_path = db_path
        self.conexion = sqlite3.connect(self.db_path)

        # SQLite no revisa las llaves foráneas por defecto. Sin esta
        # línea se podría, por ejemplo, borrar un autor que todavía
        # tiene libros asociados.
        self.conexion.execute("PRAGMA foreign_keys = ON;")

        # Para poder leer las filas por nombre de columna
        # (fila["Titulo"]) en vez de por posición.
        self.conexion.row_factory = sqlite3.Row

    def crear_tablas(self) -> None:
        """
        Crea las tres tablas del modelo relacional si todavía no
        existen, junto con la vista que usa el catálogo.
        """

        cursor = self.conexion.cursor()

        # Tabla Autor.
        # No hay un identificador natural para un autor (no se pide
        # DNI de autor en el enunciado), así que hace falta otra
        # forma de no registrar a la misma persona dos veces. Para
        # eso se guarda nombre_normalizado: nombre y apellido en
        # minúsculas y sin tildes, de modo que "García Márquez" y
        # "garcia marquez" caen en el mismo valor. La restricción
        # UNIQUE se pone sobre esa columna y no sobre Nombre/Apellido
        # directamente, porque SQLite compara texto de forma literal
        # y no ignora acentos por su cuenta.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Autor (
                IDAutor INTEGER PRIMARY KEY AUTOINCREMENT,
                Nombre TEXT NOT NULL,
                Apellido TEXT NOT NULL,
                Fecha_nacimiento DATE,
                nombre_normalizado TEXT NOT NULL UNIQUE
            );
        """)

        # Tabla Libro.
        # El ISBN se usa como identificador natural del libro porque
        # así lo pide el enunciado para detectar duplicados, por eso
        # es UNIQUE. AutorID es NOT NULL porque se asume que todo
        # libro que entra al sistema ya tiene un autor identificado;
        # no se admiten libros sin autor registrado. ON DELETE
        # RESTRICT evita borrar un autor mientras tenga libros en el
        # catálogo, para no dejar copias huérfanas.
        # El año de publicación no se valida aquí (que no sea futuro):
        # eso se revisa en Python antes de insertar, dentro de
        # agregar_libro(), porque el motor no conoce "hoy" de forma
        # simple al declarar una tabla.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Libro (
                IDLibro INTEGER PRIMARY KEY AUTOINCREMENT,
                ISBN TEXT NOT NULL UNIQUE,
                Titulo TEXT NOT NULL,
                Anio_publicacion INTEGER CHECK (Anio_publicacion > 0),
                cantidad_disponible INTEGER NOT NULL DEFAULT 0
                    CHECK (cantidad_disponible >= 0),
                AutorID INTEGER NOT NULL,
                FOREIGN KEY (AutorID) REFERENCES Autor(IDAutor)
                    ON DELETE RESTRICT
                    ON UPDATE CASCADE
            );
        """)

        # Tabla Usuario.
        # El DNI es único y de 8 dígitos numéricos, tal como pide el
        # enunciado. Se valida en dos capas: aquí con CHECK y GLOB,
        # como última barrera a nivel de base de datos, y también
        # antes en Python (crear_usuario) para poder mostrar un
        # mensaje de error más claro sin depender del texto crudo
        # del error de SQLite. El email es obligatorio pero no único,
        # porque se asume que podría haber usuarios que comparten un
        # correo (por ejemplo, familiar). El teléfono queda opcional,
        # y la fecha de membresía toma la fecha actual si no se
        # indica otra.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Usuario (
                IDUsuario INTEGER PRIMARY KEY AUTOINCREMENT,
                DNI TEXT NOT NULL UNIQUE
                    CHECK (
                        length(DNI) = 8
                        AND DNI GLOB '[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]'
                    ),
                Nombre TEXT NOT NULL,
                Apellido TEXT NOT NULL,
                email TEXT NOT NULL,
                telefono TEXT,
                fecha_membresia DATE NOT NULL DEFAULT (date('now'))
            );
        """)

        # Vista del catálogo: junta Libro y Autor para que la
        # búsqueda pueda consultar título y autor (las dos relaciones
        # que pide el Ejercicio 3) con una sola sentencia.
        cursor.execute("""
            CREATE VIEW IF NOT EXISTS CatalogoView AS
            SELECT
                L.IDLibro,
                L.ISBN,
                L.Titulo,
                L.Anio_publicacion,
                L.cantidad_disponible,
                A.IDAutor,
                A.Nombre AS AutorNombre,
                A.Apellido AS AutorApellido
            FROM Libro L
            JOIN Autor A ON L.AutorID = A.IDAutor;
        """)

        self.conexion.commit()

    def cerrar(self) -> None:
        """Cierra la conexión a la base de datos."""
        self.conexion.close()

    @staticmethod
    def _normalizar(texto: str) -> str:
        """
        Pasa un texto a minúsculas y le quita las tildes, para poder
        comparar "García" con "garcia" o "GARCIA" como si fueran lo
        mismo. La usan tanto la deduplicación de autores como la
        búsqueda del catálogo.
        """
        import unicodedata

        texto = texto.strip().lower()
        sin_tildes = unicodedata.normalize("NFKD", texto)
        return "".join(
            caracter for caracter in sin_tildes
            if not unicodedata.combining(caracter)
        )

    # Ejercicio 2 (Parte 2): añadir libros / inventario nuevo.
    def agregar_libro(
        self,
        isbn: str,
        titulo: str,
        anio_publicacion: int,
        cantidad_nueva: int,
        autor_nombre: str,
        autor_apellido: str,
        autor_fecha_nacimiento: Optional[str] = None,
    ) -> None:
        """
        Registra un libro nuevo o, si el ISBN ya existe, suma copias
        al stock sin volver a crear el libro ni el autor.

        La cantidad a agregar debe ser al menos 1, y el año de
        publicación no puede ser posterior al actual (esto se valida
        aquí mismo, en Python, comparando contra date.today().year,
        en vez de usar un trigger de SQLite: para el volumen de datos
        de este sistema no hay ninguna ganancia real en resolverlo a
        nivel de motor, y así queda más simple de leer y de explicar
        si alguien pregunta por qué falla).

        Si el libro ya existe (por ISBN) solo se actualiza el stock.
        Si no existe, se busca primero si el autor ya está registrado
        comparando nombre_normalizado directamente en SQL, y recién
        con el AutorID resuelto se inserta el libro.
        """

        if cantidad_nueva < 1:
            raise ValueError(
                "La cantidad de copias a agregar debe ser al menos 1."
            )

        if anio_publicacion > date.today().year:
            raise ValueError(
                f"El año de publicación ({anio_publicacion}) no puede "
                f"ser posterior al año actual ({date.today().year})."
            )

        cursor = self.conexion.cursor()

        # ¿El libro ya existe? Se busca por ISBN porque es el
        # identificador natural del libro según el enunciado.
        cursor.execute(
            "SELECT IDLibro, cantidad_disponible FROM Libro WHERE ISBN = ?",
            (isbn,),
        )
        libro_existente = cursor.fetchone()

        if libro_existente is not None:
            nueva_cantidad = libro_existente["cantidad_disponible"] + cantidad_nueva
            cursor.execute(
                "UPDATE Libro SET cantidad_disponible = ? WHERE IDLibro = ?",
                (nueva_cantidad, libro_existente["IDLibro"]),
            )
            self.conexion.commit()
            print(
                f"El ISBN {isbn} ya estaba en el catálogo. "
                f"Se agregaron {cantidad_nueva} copia(s); "
                f"stock actual: {nueva_cantidad}."
            )
            return

        # El libro no existe. Se arma la misma clave normalizada que
        # usa la restricción UNIQUE de Autor y se consulta directo.
        clave_autor = f"{self._normalizar(autor_nombre)} {self._normalizar(autor_apellido)}"

        cursor.execute(
            "SELECT IDAutor FROM Autor WHERE nombre_normalizado = ?",
            (clave_autor,),
        )
        fila_autor = cursor.fetchone()

        autor_es_nuevo = fila_autor is None

        if autor_es_nuevo:
            cursor.execute(
                """
                INSERT INTO Autor (Nombre, Apellido, Fecha_nacimiento, nombre_normalizado)
                VALUES (?, ?, ?, ?)
                """,
                (autor_nombre, autor_apellido, autor_fecha_nacimiento, clave_autor),
            )
            autor_id = cursor.lastrowid
        else:
            autor_id = fila_autor["IDAutor"]

        # Recién ahora, con el AutorID resuelto, se inserta el libro.
        cursor.execute(
            """
            INSERT INTO Libro (ISBN, Titulo, Anio_publicacion, cantidad_disponible, AutorID)
            VALUES (?, ?, ?, ?, ?)
            """,
            (isbn, titulo, anio_publicacion, cantidad_nueva, autor_id),
        )

        # El commit va al final, cuando autor y libro ya se
        # insertaron sin errores. Así, si algo falla a mitad de
        # camino, no queda un autor guardado sin su libro, y los
        # mensajes de confirmación de más abajo solo se imprimen
        # cuando la transacción quedó guardada de verdad.
        self.conexion.commit()

        if autor_es_nuevo:
            print(f"Autor nuevo registrado: {autor_nombre} {autor_apellido} (ID {autor_id}).")
        print(f"Libro nuevo registrado: '{titulo}' (ISBN {isbn}), {cantidad_nueva} copia(s).")

    # Ejercicio 3 (Parte 2): consultar el catálogo de libros.
    def buscar_catalogo(self, termino: str) -> list[dict]:
        """
        Busca en CatalogoView (la vista que junta Libro y Autor)
        cualquier libro cuyo título o autor contenga el término
        buscado, sin importar tildes ni mayúsculas.

        Se trae todo el catálogo y se filtra en Python con la misma
        función de normalización de agregar_libro, en vez de intentar
        una comparación con acentos directamente en SQL: SQLite no
        trae collation con normalización Unicode sin una extensión
        externa, así que hacerlo en Python es lo más simple.
        """

        cursor = self.conexion.cursor()
        cursor.execute("SELECT * FROM CatalogoView")
        filas = cursor.fetchall()

        termino_normalizado = self._normalizar(termino)
        resultados = []

        for fila in filas:
            titulo_normalizado = self._normalizar(fila["Titulo"])
            autor_normalizado = self._normalizar(
                f"{fila['AutorNombre']} {fila['AutorApellido']}"
            )

            coincide_titulo = termino_normalizado in titulo_normalizado
            coincide_autor = termino_normalizado in autor_normalizado

            if coincide_titulo or coincide_autor:
                resultados.append({
                    "autor": f"{fila['AutorNombre']} {fila['AutorApellido']}",
                    "titulo": fila["Titulo"],
                    "cantidad_disponible": fila["cantidad_disponible"],
                })

        if resultados:
            print(f"Se encontraron {len(resultados)} resultado(s) para '{termino}':")
            for r in resultados:
                print(f"  {r['titulo']}, de {r['autor']} (disponibles: {r['cantidad_disponible']})")
        else:
            print(f"No hay resultados para '{termino}'.")

        return resultados

    # Ejercicio 4 (Parte 2): crear usuarios.
    def crear_usuario(
        self,
        dni: str,
        nombre: str,
        apellido: str,
        email: str,
        telefono: Optional[str] = None,
        fecha_membresia: Optional[str] = None,
    ) -> Optional[int]:
        """
        Registra un usuario nuevo. El formato del DNI se valida
        primero en Python, para poder dar un mensaje de error
        específico, y la restricción UNIQUE de la tabla queda como
        última línea de defensa contra un DNI repetido.
        """

        import re

        if not re.fullmatch(r"\d{8}", dni):
            raise ValueError("El DNI debe tener exactamente 8 dígitos numéricos.")

        cursor = self.conexion.cursor()

        try:
            if fecha_membresia:
                cursor.execute(
                    """
                    INSERT INTO Usuario (DNI, Nombre, Apellido, email, telefono, fecha_membresia)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (dni, nombre, apellido, email, telefono, fecha_membresia),
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO Usuario (DNI, Nombre, Apellido, email, telefono)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (dni, nombre, apellido, email, telefono),
                )

            self.conexion.commit()
            nuevo_id = cursor.lastrowid
            print(f"Usuario '{nombre} {apellido}' registrado con ID {nuevo_id}.")
            return nuevo_id

        except sqlite3.IntegrityError:
            self.conexion.rollback()
            print(f"No se pudo registrar: ya existe un usuario con DNI {dni}.")
            return None
