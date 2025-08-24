import sqlite3
import os

class PeliculaDAO:
    """Clase DAO para gestionar la tabla de peliculas."""
    
    def __init__(self, database):
        """
        Inicializa la conexión a la base de datos SQLite.
        Si la base de datos no existe, se creará automáticamente.
        
        Args:
            database: Nombre del archivo de base de datos SQLite
        """
        # Verificar si la base de datos ya existe
        db_exists = os.path.exists(database)
        if db_exists:
            print(f"Conectando a base de datos existente: {database}")
        else:
            print(f"Creando nueva base de datos: {database}")
            
        self.conn = sqlite3.connect(database)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.crear_tabla()
        

    def _ejecutar_consulta(self, consulta, datos=None):
        """Método auxiliar para ejecutar consultas."""
        cursor = self.conn.cursor()
        try:
            if datos:
                cursor.execute(consulta, datos)
            else:
                cursor.execute(consulta)
            self.conn.commit()
            return cursor
        except sqlite3.Error as error:
            print(f"Error al ejecutar la consulta: {error}")
            return None

    def crear_tabla(self):
        """Crea la tabla de peliculas si no existe."""
        try:
            self._ejecutar_consulta("""
            CREATE TABLE IF NOT EXISTS peliculas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre VARCHAR(50),
                director VARCHAR(50),
                anio INT
            )""")
            print("Tabla 'peliculas' creada o ya existente.")
        except sqlite3.Error as error:
            print(f"Error al crear la tabla: {error}")

    def insertar_pelicula(self, pelicula):
        """Inserta una película en la tabla."""
        try:
            datos = (pelicula.nombre, pelicula.director, pelicula.anio)
            consulta = "INSERT INTO peliculas (nombre, director, anio) VALUES (?, ?, ?)"
            cursor = self._ejecutar_consulta(consulta, datos)
            print(f"Película '{pelicula.nombre}' insertada correctamente.")
            return True
        except sqlite3.Error as error:
            print(f"Error al insertar película: {error}")
            return False

    def obtener_todas_las_peliculas(self):
        """Obtiene y devuelve todas las peliculas."""
        try:
            cursor = self._ejecutar_consulta("SELECT * FROM peliculas")
            return cursor.fetchall()
        except sqlite3.Error as error:
            print(f"Error al obtener películas: {error}")
            input("Presiona Enter para salir...")
        self.conn.close()
        exit(1)

  
    def eliminar_pelicula(self, id_pelicula):
        """Elimina pelicula por su ID."""
        try:
            consulta = "DELETE FROM peliculas WHERE id = ?"
            cursor = self._ejecutar_consulta(consulta, (id_pelicula,))
            if cursor and cursor.rowcount > 0:
                return f"Película con ID {id_pelicula} eliminada correctamente."
            else:
                return f"No se encontró película con ID {id_pelicula}."
        except sqlite3.Error as error:
            print(f"Error al eliminar película: {error}")
            return f"Error al eliminar película: {error}"



    def cerrar_conexion(self):
        """Cierra la conexión a la base de datos."""
        self.conn.close()
        print("Conexión a la base de datos cerrada.")
